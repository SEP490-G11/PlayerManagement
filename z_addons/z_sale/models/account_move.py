# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class ZAccountMove(models.Model):
    _inherit = "account.move"

    so_id = fields.Many2one("sale.order", string="Source SO", readonly=True, copy=False)

    def action_post(self):
        res = super(ZAccountMove, self).action_post()
        if (
            self.move_type == "out_invoice"
            and not self.sale_order_count
            and not self.so_id
        ):
            so_vals = {
                "partner_id": self.partner_id.id,
                "from_invoice_order": True,
                "order_line": self._prepare_order_lines_from_invoice(self),
            }
            so = self.env["sale.order"].create(so_vals)
            so.action_confirm()

            for order_line in so.order_line:
                order_line.write({"order_id": so.id})

            self.write({"so_id": so.id})

        purchased_combo = self.env["z_combo.purchased.combo.line"]
        for rec in self.invoice_line_ids:
            if rec.combo_id and rec.product_id.detailed_type == "service":
                for _ in range(int(rec.quantity)):
                    purchased_combo.create(
                        {
                            "partner_id": self.partner_id.id,
                            "combo_id": rec.combo_id.id,
                            "product_id": rec.product_id.id,
                            "quantity": 1,
                            "account_move_id": self.id,
                            "sub_combo_id": rec.sub_combo_id.id,
                        }
                    )
            if rec.combo_id and rec.product_id.detailed_type == "product":
                purchased_combo.create(
                    {
                        "partner_id": self.partner_id.id,
                        "combo_id": rec.combo_id.id,
                        "product_id": rec.product_id.id,
                        "quantity": rec.quantity,
                        "account_move_id": self.id,
                        "sub_combo_id": rec.sub_combo_id.id,
                    }
                )

        return res

    def _prepare_order_lines_from_invoice(self, invoice):
        """Prepare the Sale Order lines based on the Invoice lines."""
        order_lines = []
        for line in invoice.invoice_line_ids:
            if line.product_id and line.quantity > 0:
                order_lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "product_uom_qty": line.quantity,  # Use the quantity from the invoice line
                            "price_unit": line.price_unit,  # Use the price from the invoice line
                            "name": line.name
                            or line.product_id.name,  # Use name from the invoice line
                            "invoice_lines": [
                                (4, line.id)
                            ],  # Link the invoice line to the SO line
                        },
                    )
                )
        return order_lines

    def write(self, vals):
        if "so_id" in vals and any(move.so_id for move in self):
            raise ValidationError(
                _(
                    "You cannot modify the 'Source SO' for invoices created from a Sale Order."
                )
            )

        return super(ZAccountMove, self).write(vals)

    def button_cancel(self):
        # Shortcut to move from posted to cancelled directly. This is useful for E-invoices that must not be changed
        # when sent to the government.

        entry_payments = self.env["account.payment"].search(
            [("reconciled_invoice_code", "=", self.code)]
        )
        entry_am = entry_payments.move_id

        for line in entry_am.line_ids:
            line.remove_move_reconcile()
        for rec in entry_payments:
            rec.sudo().unlink()

        self.so_id.set_cancel()

        # Handle related pickings (Delivery Orders)
        for picking in self.so_id.picking_ids:
            if picking.state == "done":
                # Create the return wizard
                return_wizard = self.env["stock.return.picking"].create(
                    {
                        "picking_id": picking.id,
                    }
                )
                # Confirm the return
                return_wizard._create_returns()
            else:
                # Cancel pickings that are not in 'done' state
                picking.action_cancel()

        moves_to_reset_draft = self.filtered(lambda x: x.state == "posted")
        if moves_to_reset_draft:
            moves_to_reset_draft.button_draft()

        if any(move.state != "draft" for move in self):
            raise UserError(_("Only draft journal entries can be cancelled."))

        self.write({"auto_post": "no", "state": "cancel"})

    @api.model
    def cron_generate_so_from_invoices(self):
        """Hàm cron để tạo SO từ hóa đơn chưa có so_id"""
        invoices = self.env["account.move"].search(
            [
                ("so_id", "=", False),  # Chưa có SO
                ("move_type", "=", "out_invoice"),  # Chỉ lấy hóa đơn bán hàng
                ("state", "in", ["draft", "posted", "cancel"]),  # Lọc hóa đơn cần xử lý
            ]
        )

        for invoice in invoices:
            try:
                sale_order = self._create_sale_order_from_invoice(invoice)
                if not invoice.so_id:
                    invoice.write({"so_id": sale_order.id})
                _logger.info(f"Đã tạo SO {sale_order.name} từ hóa đơn {invoice.name}")
            except Exception as e:
                _logger.error(f"Lỗi khi tạo SO từ hóa đơn {invoice.name}: {e}")

    def _create_sale_order_from_invoice(self, invoice):
        """Tạo SO từ hóa đơn mà KHÔNG sinh DO"""
        sale_order_obj = self.env["sale.order"]
        so_vals = {
            "move_count": 1,
            "invoice_count": 1,
            "place_id": invoice.place_id.id,
            "z_appointment_id": invoice.z_appointment_id.id,
            "partner_id": invoice.partner_id.id,  # Khách hàng
            "date_order": invoice.invoice_date or fields.Datetime.now(),  # Ngày tạo SO
            "order_line": [
                (0, 0, self._prepare_sale_order_line(line))
                for line in invoice.invoice_line_ids
            ],
            "state": "draft",  # Để SO ở trạng thái nháp trước
        }
        sale_order = sale_order_obj.create(so_vals)
        invoice.write(
            {
                "so_id": sale_order.id,
                "sale_order_count": 1,  # Cập nhật số lượng SO để hiển thị Smart Button
            }
        )
        # Chuyển trạng thái của SO mà KHÔNG sinh DO
        if invoice.state in ["draft", "posted"]:
            sale_order.write(
                {"state": "sale"}
            )  # Đánh dấu là đã xác nhận mà không chạy action_confirm
        elif invoice.state == "cancel":
            sale_order.action_cancel()  # Nếu hóa đơn bị hủy, cũng hủy SO

        return sale_order

    def _prepare_sale_order_line(self, line):
        """Chuyển đổi dòng hóa đơn thành dòng SO"""
        return {
            "product_id": line.product_id.id,
            "product_uom_qty": line.quantity,
            "price_unit": line.price_unit,
            "tax_id": [(6, 0, line.tax_ids.ids)],
            "invoice_lines": [(4, line.id)],
        }
