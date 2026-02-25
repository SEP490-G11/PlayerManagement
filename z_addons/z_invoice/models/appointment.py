# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class ZAppointment(models.Model):
    _inherit = "z_appointment.appointment"
    _order = "booking_date desc, get_examination_code desc"

    z_invoice_ids = fields.One2many(
        "account.move",
        "z_appointment_id",
        "Invoices",
    )

    z_invoice_status = fields.Selection(
        [
            ("draft", _("Draft")),
            ("half", _("Half buy")),
            ("full", _("Full buy")),
            ("unpaid", _("Unpaid")),
        ],
        string="TTTT",
        compute="_compute_z_invoice_status",
        store=True,
    )
    has_invoice = fields.Boolean("Has invoice", compute="_compute_has_invoice")

    @api.depends("z_invoice_ids", "z_invoice_ids.payment_state")
    def _compute_z_invoice_status(self):
        for rec in self:
            invoices = rec.z_invoice_ids
            if not invoices:
                rec.z_invoice_status = False
            else:
                draft_invoices = invoices.filtered(lambda inv: inv.state == "draft")
                paid_invoices = invoices.filtered(
                    lambda inv: inv.payment_state == "paid"
                )
                partially_paid_invoices = invoices.filtered(
                    lambda inv: inv.payment_state == "partial"
                )
                unpaid_invoices = invoices.filtered(
                    lambda inv: inv.payment_state == "not_paid"
                    and inv.state == "posted"
                )

                total_amount = sum(invoices.mapped("amount_total_signed"))
                total_paid = sum(invoices.mapped("paid"))

                if draft_invoices and not paid_invoices and not partially_paid_invoices:
                    rec.z_invoice_status = "draft"
                elif (
                    unpaid_invoices
                    and not draft_invoices
                    and not paid_invoices
                    and not partially_paid_invoices
                ):
                    rec.z_invoice_status = "unpaid"
                elif partially_paid_invoices or (draft_invoices and paid_invoices):
                    rec.z_invoice_status = "half"
                elif total_paid >= total_amount:
                    rec.z_invoice_status = "full"
                else:
                    rec.z_invoice_status = "half"

    get_examination_code = fields.Char(
        compute="_compute_get_examination_code", store=True
    )

    @api.depends("z_invoice_ids")
    def _compute_has_invoice(self):
        for rec in self:
            rec.has_invoice = len(rec.z_invoice_ids) > 0

    @api.depends("examination_code")
    def _compute_get_examination_code(self):
        for rec in self:
            rec.get_examination_code = (
                "%s" % rec.examination_code if rec.examination_code else False
            )

    def action_create_invoices(self):
        if int(self.state) == 1:
            raise ValidationError("Trạng thái 'Chưa đến' không thể tạo hoá đơn")
        return {
            "type": "ir.actions.act_window",
            "name": "Thanh toán",
            "view_mode": "form",
            "res_model": "account.move",
            "res_id": None,
            "id": self.env.ref("account.action_move_out_invoice_type").id,
            "context": {
                "default_partner_id": self.customer_id.id,
                "default_partner_dob": self.customer_id.date,
                "default_partner_address": self.customer_id.street,
                "default_partner_job": self.customer_id.job,
                "default_move_type": "out_invoice",
                "default_z_appointment_id": self.id,
                "default_company_id": self.env.company.id,
                "linked_from_appointment": True,
            },
            "target": "current",
        }

    @api.depends("get_examination_code")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                "%s" % rec.get_examination_code if rec.get_examination_code else False
            )
