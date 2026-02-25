# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class ZSaleOrder(models.Model):
    _inherit = "sale.order"

    place_id = fields.Many2one(
        "z_place.place",
        string="Place",
        required=True,
        default=lambda self: self.get_default_place_id(),
    )

    def get_default_place_id(self):
        place = self.env["z_place.place"].search([], limit=1)
        if place:
            return place.id
        return False

    from_invoice_order = fields.Boolean(default=False)
    move_count = fields.Integer(default=0)

    z_appointment_id = fields.Many2one(
        "z_appointment.appointment", string="Appointment"
    )

    partner_name = fields.Char(
        string="Partner name", compute="_compute_partner_name", store=True
    )
    partner_fullname = fields.Char(
        string="Full name", related="partner_id.name", store=True
    )
    partner_group = fields.Char(string="Group", related="partner_id.group_id.name")
    partner_code = fields.Char(string="Partner code", related="partner_id.code")
    partner_gender = fields.Selection(string="Gender", related="partner_id.gender")
    partner_dob = fields.Date(
        string="Date of birth", related="partner_id.date", default=False
    )
    partner_mobile = fields.Char(string="Phone number", related="partner_id.mobile")
    partner_z_mobile = fields.Char(string="Phone number", related="partner_id.z_mobile")
    partner_job = fields.Char(string="Job", related="partner_id.job")
    partner_address = fields.Char(
        string="Address", related="partner_id.street", store=False
    )
    appointment_place = fields.Boolean(default=False)
    combo_line_ids = fields.Many2many("z_combo.combo")

    @api.depends("partner_id")
    def _compute_partner_name(self):
        for record in self:
            record.partner_name = record.partner_id.extra_name

    def action_create_invoice(self):
        invoices = self._create_invoices(final=True, grouped=not True)
        invoices.write(
            {
                "so_id": self.id,
                "place_id": self.place_id,
                "z_appointment_id": self.z_appointment_id,
                "combo_line_ids": (
                    [(6, 0, self.combo_line_ids.ids)] if self.combo_line_ids else False
                ),
            }
        )
        return self.action_view_invoice(invoices=invoices)

    show_create_invoice_button = fields.Boolean(
        compute="_compute_show_create_invoice_button",
        string="Show Create Invoice Button",
    )

    @api.onchange("z_appointment_id")
    def _onchange_z_appointment_id_place(self):
        self.place_id = (
            self.z_appointment_id.place_id if self.z_appointment_id else False
        )
        self.appointment_place = True if self.z_appointment_id else False

    @api.depends("state")
    def _compute_show_create_invoice_button(self):
        for order in self:
            order.show_create_invoice_button = (
                order.invoice_status != "to invoice"
                or order.from_invoice_order
                or order.state in ["draft", "cancel"]
            )

    def _action_cancel(self):
        draft_invoices = self.invoice_ids.filtered(lambda inv: inv.state == "draft")
        draft_invoices.button_cancel()
        am = self.env["account.move"].search([("id", "in", self.invoice_ids.ids)])
        entry_data = []
        aml = self.env["account.move.line"].search([("move_id", "in", am.ids)])

        payments = aml.mapped("payment_id").filtered(lambda p: p.id)
        for entry in am:
            entry_data.extend(am.mapped("code"))
        entry_payments = self.env["account.payment"].search(
            [("reconciled_invoice_code", "in", entry_data)]
        )
        entry_am = entry_payments.move_id

        for line in entry_am.line_ids:
            line.remove_move_reconcile()
        for rec in entry_payments:
            rec.sudo().unlink()

        for line in aml:
            line.remove_move_reconcile()
        for rec in payments:
            rec.sudo().unlink()
        for rec in am:
            rec.sudo().button_cancel()

        # Handle related pickings (Delivery Orders)
        for picking in self.picking_ids:
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

        # Update the sale order state
        return self.write({"state": "cancel"})

    def action_cancel(self):
        """Cancel SO after showing the cancel wizard when needed. (cfr :meth:`_show_cancel_wizard`)

        For post-cancel operations, please only override :meth:`_action_cancel`.

        note: self.ensure_one() if the wizard is shown.
        """
        if any(order.locked for order in self):
            raise UserError(
                _("You cannot cancel a locked order. Please unlock it first.")
            )
        cancel_warning = self._show_cancel_wizard()
        if cancel_warning:
            self.ensure_one()
            ctx = {
                "default_order_id": self.id,
                "mark_so_as_canceled": True,
            }
            return {
                "name": _("Cancel %s", self.type_name),
                "view_mode": "form",
                "res_model": "sale.order.cancel",
                "view_id": self.env.ref("z_sale.z_sale_order_cancel_view_form").id,
                "type": "ir.actions.act_window",
                "context": ctx,
                "target": "new",
            }
        else:
            return self._action_cancel()

    def set_cancel(self):
        self.write({"state": "cancel"})

    name = fields.Char(required=True, copy=False, readonly=True, default="New")

    @api.model
    def create(self, vals):
        """Sinh mã SO ngay khi đơn hàng được tạo"""
        if vals.get("name", "New") == "New":
            vals["name"] = self._generate_so_code()
        return super(ZSaleOrder, self).create(vals)

    def _generate_so_code(self):
        """Tạo số thứ tự đơn hàng theo định dạng SO/yymmdd0001 dựa trên ngày tạo"""
        today_str = datetime.today().strftime("%y%m%d")  # Lấy ngày tạo dạng yymmdd
        prefix = f"SO/{today_str}"

        # Tìm hoặc tạo sequence nếu chưa có
        sequence = (
            self.env["ir.sequence"]
            .sudo()
            .search([("code", "=", f"sale.order.daily.{today_str}")], limit=1)
        )
        if not sequence:
            sequence = (
                self.env["ir.sequence"]
                .sudo()
                .create(
                    {
                        "name": f"Daily Sale Order Sequence {today_str}",
                        "code": f"sale.order.daily.{today_str}",
                        "prefix": prefix,
                        "padding": 4,
                        "number_next": 1,  # Luôn tiếp tục từ số tiếp theo
                        "number_increment": 1,
                    }
                )
            )
        return sequence.next_by_code(f"sale.order.daily.{today_str}")

    @api.onchange("combo_line_ids")
    def _onchange_combo_line_ids(self):
        # Lọc và xoá tất cả các dòng có combo_id
        self.order_line = self.order_line.filtered(lambda x: not x.combo_id)

        new_products = self.env["sale.order.line"]
        new_items = self.combo_line_ids

        for item in new_items:
            for line in item.combo_line_ids:
                new_line = new_products.new(
                    {
                        "product_uom_qty": line.quantity,
                        "product_template_id": line.product_id.product_tmpl_id.id,
                        "price_unit": line.price_after_discount,
                        "combo_id": line.combo_id.id,
                        "sub_combo_id": line.sub_combo_id.id,
                        "product_id": line.product_id.id,
                    }
                )
                new_products += new_line
        self.order_line += new_products
