# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from odoo.addons.z_invoice.helpers.misa_utils import ZMISAUtils
import logging

_logger = logging.getLogger(__name__)


class ZAccountMove(models.Model):
    _inherit = "account.move"

    code = fields.Char(compute="_compute_code", string="Invoice code", store=True)
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
    clinic_date = fields.Char(
        string="Examination date",
        compute="_compute_clinic_date",
        readonly=True,
        store=True,
    )
    customer_detail_widget = fields.Json(
        string="Partner name", related="partner_id.customer_detail_widget"
    )
    contact_channel = fields.Char(string="Contact channel", store=True)
    medical_examiner = fields.Char(string="Examiner", store=True)
    reexaminer = fields.Char(string="Re-exam", store=True)
    diagnostic = fields.Char(
        string="Diagnostic", compute="_compute_diagnostic", store=True
    )
    note = fields.Text(string="Note")
    label = fields.Selection(
        [
            ("1", "Ortho K Pakage"),
            ("2", "Myopia Control Glasses Package"),
            ("3", "Hyperopia Package"),
            ("4", "Family Package"),
            ("5", "Updated Invoice"),
            ("6", "No label"),
        ],
        string="Invoice label",
        default=False,
    )
    amount_residual = fields.Monetary(
        string="Amount due", compute="_compute_amount", store=True, tracking=True
    )
    invoice_user_id = fields.Many2one(
        string="Salesperson",
        comodel_name="res.users",
        copy=False,
        tracking=True,
        compute="_compute_invoice_default_sale_person",
        store=True,
        readonly=False,
    )
    total_discount = fields.Float(
        string="Total discount",
        default=0,
        store=True,
        compute="_compute_total_discount",
        digits="Invoice",
    )
    # total_without_discount = fields.Float(
    #     string="Total without discount",
    #     related="invoice_line_ids.total_without_discount",
    #     default=0,
    #     store=True,
    # )
    # total_after_discount = fields.Float(
    #     string="Total after discount",
    #     compute="_compute_total_after_discount",
    #     default=0,
    # )
    price_total = fields.Monetary(
        string="Price Total", related="invoice_line_ids.price_total", store=True
    )
    payment_methods = fields.Char(
        string="Payment Method", compute="_compute_payment_methods", store=True
    )
    debt = fields.Char(string="Debt", compute="_compute_debt", store=True)
    paid = fields.Float(
        string="Paid", compute="_compute_total_paid", store=True, digits="Invoice"
    )
    creator = fields.Char(string="Creator")
    creator_account = fields.Many2one(
        string="Creator",
        comodel_name="res.users",
        default=lambda self: self.env.user.id,
    )
    combo_line_ids = fields.One2many(
        "account.combo.line", "account_move_id", string="Products in Combo", copy=True
    )
    z_appointment_id = fields.Many2one(
        "z_appointment.appointment", string="Appointment"
    )
    invoice_date = fields.Date(default=lambda self: fields.Date.today())
    amount_total_signed = fields.Float(digits="Invoice")
    amount_residual_signed = fields.Float(digits="Invoice")
    place_id = fields.Many2one("z_place.place", string="Place", required=True)
    appointment_place = fields.Boolean(default=False)
    combo_id = fields.Many2one("z_combo.combo", string="Combo")
    invoice_line_ids = fields.One2many(
        compute="_compute_invoice_line_ids", store=True, readonly=False
    )

    total_after_discount_combo = fields.Float(
        string="Tổng thanh toán combo",
        compute="_compute_total_after_discount_combo",
        store=True,
    )

    @api.depends(
        "invoice_line_ids",
        "invoice_line_ids.discount_amount",
        "invoice_line_ids.total_without_discount",
    )
    def _compute_total_after_discount_combo(self):
        for rec in self:
            total_discount = 0
            total_without_discount = 0
            for line in rec.invoice_line_ids.filtered(lambda l: l.combo_id):
                total_discount += line.discount_amount
                total_without_discount += line.quantity * line.price_unit
            rec.total_after_discount_combo = total_without_discount - total_discount

    @api.depends("combo_id")
    def _compute_invoice_line_ids(self):
        for record in self:
            # # Clear existing combo lines
            # record.invoice_line_ids = [(5, 0, 0)]
            # Clear existing combo lines
            record.invoice_line_ids = [
                (2, line.id, 0) for line in record.invoice_line_ids if line.combo_id
            ]

            if record.combo_id:
                new_invoice_lines = []
                invoice_lines = record.combo_id.combo_line_ids

                for invoice_line in invoice_lines:
                    new_invoice_lines.append(
                        (
                            0,
                            0,
                            {
                                "product_id": invoice_line.product_id.id,
                                "quantity": invoice_line.quantity,
                                "price_unit": invoice_line.price,
                                "move_id": record.id,
                                "combo_id": record.combo_id.id,
                            },
                        )
                    )

                record.invoice_line_ids = new_invoice_lines

    @api.onchange("combo_id")
    def _onchange_combo_id(self):
        if self.combo_id:
            self._compute_invoice_line_ids()

    reexam_count = fields.Integer(
        "Số lần tái khám", related="z_appointment_id.reexam_count", store=True
    )

    is_publish_vat_invoice = fields.Boolean(string="Is Publish VAT Invoice", default=False)
    amount_untaxed_before_discount = fields.Monetary(
        string="Amount Untaxed Before Discount",
        compute="_compute_amount_untaxed_before_discount",
        store=True,
        digits="Invoice",
        help="The total amount of the invoice before applying any discount and tax.",
    )
    amount_discount_lines = fields.Monetary(
        string="Total discount on account move lines",
        default=0,
        store=True,
        compute="_compute_amount_discount_lines",
        digits="Invoice",
    )
    amount_discount_promotion = fields.Monetary(
        string="Total promotion",
        default=0,
        store=True,
        compute="_compute_amount_discount_promotion",
        digits="Invoice",
    )

    @api.depends("invoice_line_ids", "invoice_line_ids.balance", "state")
    def _compute_amount_untaxed_before_discount(self):
        for rec in self:
            amount_untaxed_before_discount = 0.0
            for line in rec.invoice_line_ids:
                if line.is_promotion_line:
                    continue
                amount_untaxed_before_discount += (line.quantity * line.price_unit)
            
            rec.amount_untaxed_before_discount = amount_untaxed_before_discount
    @api.depends("invoice_line_ids", "invoice_line_ids.balance", "state")
    def _compute_amount_discount_promotion(self):
        for rec in self:
            amount_discount_promotion = 0.0
            for line in rec.invoice_line_ids:
                if line.is_promotion_line:
                    amount_discount_promotion += line.price_subtotal
            rec.amount_discount_promotion = amount_discount_promotion

    @api.depends(
            "invoice_line_ids", "invoice_line_ids.discount", 
            "invoice_line_ids.balance", "state"
            )
    def _compute_amount_discount_lines(self):
        for rec in self:
            amount_discount_lines = 0.0
            for line in rec.invoice_line_ids:
                amount_discount_lines += line.discount_amount_line
            self.amount_discount_lines = -abs(amount_discount_lines)

    @api.onchange("z_appointment_id")
    def _onchange_z_appointment_id_place(self):
        self.place_id = (
            self.z_appointment_id.place_id if self.z_appointment_id else False
        )
        self.appointment_place = True if self.z_appointment_id else False

    def js_assign_outstanding_line(self, line_id):
        """Called by the 'payment' widget to reconcile a suggested journal item to the present
        invoice.

        :param line_id: The id of the line to reconcile with the current invoice.
        """
        self.ensure_one()
        lines = self.env["account.move.line"].browse(line_id)
        for item in lines:
            if item.payment_id.amount > self.amount_residual:
                raise ValidationError(
                    _("Amount of payment is greater than amount of invoice")
                )
        lines += self.line_ids.filtered(
            lambda line: line.account_id == lines[0].account_id and not line.reconciled
        )
        return lines.reconcile()

    @api.depends("amount_residual")
    def _compute_debt(self):
        for record in self:
            record.debt = record.amount_residual

    @api.depends("price_total")
    def _compute_payment_methods(self):
        for record in self:
            if record.invoice_payments_widget:
                widget_content = record.invoice_payments_widget.get("content")
                record.payment_methods = (
                    widget_content[-1].get("journal_name", "") if widget_content else ""
                )

    @api.depends("note")
    def _compute_diagnostic(self):
        for record in self:
            record.diagnostic = record.note

    @api.depends("create_date")
    def _compute_clinic_date(self):
        for record in self:
            record.clinic_date = record.create_date.strftime("%d/%m/%Y")

    @api.depends("create_date")
    def _compute_code(self):
        sequence = self.env["account.move"].search_count(
            [("create_date", ">=", datetime.date.today().strftime("%Y-%m-%d 00:00:00"))]
        )
        for record in self:
            today = datetime.date.today()

            record.code = (
                f"HD/{today.strftime('%Y%m%d')}/{sequence:04d}"
                if record.id
                else f"HD/{today.strftime('%Y%m%d')}/False"
            )

    @api.depends("partner_id")
    def _compute_partner_name(self):
        for record in self:
            record.partner_name = record.partner_id.extra_name

    @api.depends("amount_residual")
    def _compute_total_paid(self):
        for move in self:
            total = 0
            if move.state == "posted" and move.is_invoice(include_receipts=True):
                reconciled_partials = move.sudo()._get_all_reconciled_invoice_partials()
                for reconciled_partial in reconciled_partials:
                    total += reconciled_partial["amount"]
            move.paid = total

    @api.depends("amount_discount_lines", "amount_discount_promotion")
    def _compute_total_discount(self):
        for rec in self:
            total_discount = 0
            total_discount = rec.amount_discount_lines + rec.amount_discount_promotion
            rec.total_discount = total_discount

    def merge_duplicate_product_lines(self):
        line_ids = self.invoice_line_ids.filtered(
            lambda l: l.product_id and not l.combo_id
        )
        products = line_ids.mapped("product_id")
        for product in products:
            product_lines = line_ids.filtered(lambda l: l.product_id == product)
            if len(product_lines) > 1:
                product_lines[0].quantity = sum(product_lines.mapped("quantity"))
                self.invoice_line_ids = [(2, product_lines[1:].id, 0)]

    @api.onchange("invoice_line_ids")
    def _onchange_line_ids(self):
        self.merge_duplicate_product_lines()
        combos = self.env["account.combo.line"]
        for line in self.invoice_line_ids:
            if line.product_id.is_combo:
                product_id = line.product_id.id
                combo = self.env["z_combo.combo"].search(
                    [("product_id", "=", product_id)]
                )
                combo_rel = combos.new(
                    {"account_move_id": self.id, "combo_id": combo.id}
                )
                combos += combo_rel
        self.combo_line_ids = combos

    # @api.depends("total_without_discount", "total_discount")
    # def _compute_total_after_discount(self):
    #     self.total_after_discount = self.total_without_discount - self.total_discount

    def button_export_invoice(self):
        action = self.env["ir.actions.report"]._for_xml_id(
            "z_invoice.action_report_account_invoice"
        )
        return action

    def action_open_update(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Update Invoice"),
            "view_mode": "form",
            "view_id": self.env.ref("z_invoice.form_view_account_move_update").id,
            "res_model": "account.move",
            "res_id": self.id,
            "context": {},
            "target": "new",
        }

    def action_post(self):
        try:
            moves_with_payments = self.filtered("payment_id")
            other_moves = self - moves_with_payments
            if moves_with_payments:
                moves_with_payments.payment_id.action_post()
            if other_moves:
                other_moves._post(soft=False)
        except Exception as e:
            notification = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "danger",
                    "message": e,
                },
            }
            return notification
        return False

    @api.depends("code")
    def _compute_display_name(self):
        for rec in self:
            if rec.code:
                rec.display_name = "%s" % rec.code

    def action_print(self):
        action = self.env["ir.actions.report"]._for_xml_id(
            "z_invoice.action_report_account_invoice"
        )
        return action

    # ==========================MISA=================================

    is_publish_vat_invoice = fields.Boolean(
        string="Is Publish VAT Invoice", default=False
    )
    is_call_to_misa = fields.Boolean(
        string="Is Call to MISA", default=False
    )
    misa_url = fields.Char(string="URL")
    misa_is_ticket = fields.Boolean(string="Is Ticket", default=False)
    misa_transaction_id = fields.Char(string="Transaction ID")
    misa_inv_no = fields.Char(string="MISA Invoice No")
    misa_inv_code = fields.Char(string="MISA Invoice Code")
    misa_state = fields.Selection(
        [
            ("draft", _("Draft")),
            ("published", _("Published")),
            ("cancelled", _("Cancelled")),
        ],
        string="MISA State",
        default="draft",
        tracking=True,
    )

    misa_type_inv = fields.Selection(
        [
            ("0", _("Normal")),
            ("1", _("Replace")),
            ("2", _("Adjust")),
            ("3", _("Cancel")),
        ],
        string="MISA Type Invoice",
        default="0",
        compute="_compute_misa_type_inv",
        store=True,
    )
    origin_move_id = fields.Many2one(
        "account.move",
        string="Origin Move",
        help="The original move that is being reversed or replaced",
    )
    is_cancel_misa_inv = fields.Boolean(string="Can Publish MISA Invoice", default=True)
    can_publish_misa_invoice = fields.Boolean(
        string="Can Publish MISA Invoice", default=True
    )
    misa_template_id = fields.Many2one(
        "z_invoice.misa_invoice_template", string="MISA Template"
    )
    
    cancel_attach_move_id = fields.Many2one(
        "account.move", string="Cancel Attach Move", help="The move that is being cancelled"
    )
    able_to_refunds_or_modify = fields.Boolean(
        string="Able to refunds or modify",
        compute="_compute_able_to_refunds_or_modify",
    )
    
    @api.depends("publish_misa_invoice_date")
    def _compute_able_to_refunds_or_modify(self):
        for record in self:
            if record.publish_misa_invoice_date:
                current_date = fields.Date.today()
                invoice_date = record.publish_misa_invoice_date  
                days_diff = (current_date - invoice_date).days
                record.able_to_refunds_or_modify = days_diff <= 1
            else:
                record.able_to_refunds_or_modify = False

    can_send_email = fields.Boolean(
        string="Can Send Email", 
        compute="_compute_can_send_email",
        store=True,
        help="Whether this published invoice can send email"
    )
    
    publish_misa_invoice_date = fields.Date(
        string = "Publish MISA Invoice Date",
        default = False,
    )
    email_sent = fields.Boolean(
        string="Email Sent",
        default=False,
        help="Whether email has been sent for this invoice"
    )
    is_creator = fields.Boolean(
        string="Is Creator",
        compute="_compute_is_creator",
        help="Whether current user is the invoice creator"
    )
    
    @api.depends("create_uid")
    def _compute_is_creator(self):
        for record in self:
            record.is_creator = record.create_uid.id == self.env.user.id
    
    
    @api.depends(
        "origin_move_id", "reversal_move_id", "move_type", "is_cancel_misa_inv"
    )
    def _compute_misa_type_inv(self):
        for record in self:
            if not record.is_cancel_misa_inv:
                record.misa_type_inv = "3"
            elif record.origin_move_id and record.move_type == "out_invoice":
                record.misa_type_inv = "1"
            elif record.reversed_entry_id and record.move_type == "out_refund":
                record.misa_type_inv = "2"
            else:
                record.misa_type_inv = "0"

    def action_open_publish_misa_invoice_form(self):
        self.ensure_one()
        if self.misa_state == "published":
            raise ValidationError(_("Invoice has been published"))

        if self.misa_type_inv in ["1", "2"]: 
            original_invoice = None
            if self.misa_type_inv == "1":  
                original_invoice = self.origin_move_id
            elif self.misa_type_inv == "2": 
                original_invoice = self.reversed_entry_id
            
            if original_invoice and original_invoice.publish_misa_invoice_date:
                current_date = fields.Date.today()
                original_date = original_invoice.publish_misa_invoice_date
                days_diff = (current_date - original_date).days
                
                if days_diff > 1:
                    raise ValidationError(_(
                        "Hóa đơn %s chỉ có thể được phát hành trong vòng 1 ngày kể từ ngày hóa đơn gốc (%s). "
                        "Hiện tại đã qua %d ngày." % (
                            "thay thế" if self.misa_type_inv == "1" else "điều chỉnh",
                            original_date.strftime("%d/%m/%Y"),
                            days_diff
                        )
                    ))

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "z_invoice.action_account_move_misa_issuance_wizard"
        )
        action["context"] = {
            "name": _("VAT Invoice"),   
            "default_move_id": self.id,
            "default_misa_template_id": self.misa_template_id.id,
        }
        return action

    def action_send_published_invoice_email(self):
        self.ensure_one()
        
        # Check if transaction ID exists
        if not self.misa_transaction_id:
            raise ValidationError(_("Transaction ID is not exist"))
        
        # Open the email wizard
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "z_invoice.action_account_move_email_wizard"
        )
        action["context"] = {
            "default_move_id": self.id,
        }
        return action
    
    
    def reget_misa_url(self):
        self.ensure_one()
        if not self.misa_transaction_id:
            raise ValidationError(_("Transaction ID is not exist"))
        
        token = self._get_misa_token()
        response = ZMISAUtils.call_preview_published_invoice_api(token, [self.misa_transaction_id], self.env)
        if response.get("success") and response.get("data"):
                preview_url = response["data"]
                if preview_url:
                    self.misa_url = preview_url
        else:
            raise ValidationError(response.get("ErrorCode") or "Gặp lỗi trong quá trình lấy URL.")
    
    
    def button_cancel(self):
        _logger.info(f"button_cancel called for invoice {self.code} with misa_state: {self.misa_state}")
        if self.misa_state == "published":
            _logger.warning(f"Cannot cancel published invoice: {self.code}")
            raise ValidationError(_("Cannot cancel invoice. Invoice has been published to MISA."))
        
        if self.cancel_attach_move_id:
            self.cancel_attach_move_id.button_cancel()
        _logger.info(f"Proceeding with cancel for invoice: {self.code}")
        return super(ZAccountMove, self).button_cancel()

    def _get_misa_token(self, get_new=False):
        if not self.place_id:
            raise ValidationError(_("Place is not set. Cannot retrieve MISA token."))
        if get_new:
            return self.place_id._get_new_token()
        else:
            return self.place_id.auth_token or self.place_id._get_new_token()
    
    @api.depends('misa_state', 'misa_transaction_id', 'partner_id.email')
    def _compute_can_send_email(self):
        for record in self:
            record.can_send_email = (
                record.misa_state == 'published' and 
                record.misa_transaction_id and 
                record.partner_id.email
            )

    def unlink(self):
        """Override unlink method to check delete permissions"""
        raise ValidationError(_("Hiện tại không hỗ trợ tính năng này."))
        return super(ZAccountMove, self).unlink()