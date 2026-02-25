# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from datetime import timedelta
from odoo.exceptions import ValidationError


class ZComboOrder(models.Model):
    _name = "z_combo.combo.order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Combo Order"
    _rec_name = "invoice_code"

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        domain="[('is_customer','=', True)]",
        required=True,
    )
    combo_id = fields.Many2one(
        comodel_name="z_combo.combo", string="Combo", required=True
    )
    is_done = fields.Boolean(string="Done", default=False)
    invoice_code = fields.Char(string="Invoice Code", size=15, required=True)
    registration_date = fields.Date(string="Registration Date", required=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    expiration_date = fields.Date(
        string="Expiration Date",
        compute="_compute_expiration_date",
        store=True,
    )
    last_expiration_date = fields.Date(
        string="The last expiration date",
        compute="_compute_last_expiration_date",
    )
    session_count = fields.Integer(string="Number of Sessions")
    status = fields.Selection(
        [("not paid", _("Not Paid")), ("paid", _("Paid")), ("deposit", _("Deposit"))],
        string="Status",
        default="not paid",
        tracking=True,
    )
    note = fields.Text(string="Note")
    tracking_date = fields.Date(string="Tracking Date")

    @api.depends("start_date", "combo_id.validity_days")
    def _compute_expiration_date(self):
        for record in self:
            if record.start_date and record.combo_id.validity_days:
                record.expiration_date = record.start_date + timedelta(
                    days=record.combo_id.validity_days
                )
            else:
                record.last_expiration_date = False
                
    
    @api.depends("start_date", "combo_id.validity_days")
    def _compute_last_expiration_date(self):
        for record in self:
            if record.start_date and record.combo_id.validity_days:
                record.last_expiration_date = record.start_date + timedelta(
                    days=record.combo_id.validity_days - 1
                )
            else:
                record.last_expiration_date = False

    @api.constrains("start_date", "end_date", "registration_date")
    def validate_date(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.start_date > rec.end_date:
                raise ValidationError(_("End date is must be greater than start date"))
            if (
                rec.start_date
                and rec.registration_date
                and rec.start_date < rec.registration_date
            ):
                raise ValidationError(
                    _("Start date is must be greater than registration date")
                )
            if (
                rec.registration_date
                and rec.end_date
                and rec.registration_date > rec.end_date
            ):
                raise ValidationError(
                    _("End date is must be greater than registration date")
                )
            if (
                rec.last_expiration_date
                and rec.end_date
                and rec.last_expiration_date < rec.end_date
            ):
                raise ValidationError(
                    _("End date is must be smaller than last expiration date")
                )

    @api.constrains("invoice_code")
    def _check_code(self):
        for rec in self:
            if len(self.search([("invoice_code", "=", rec.invoice_code)])) > 1:
                raise ValidationError(_("Invoice code is must be unique"))
            if not re.match("^[A-Z0-9/]{1,15}$", rec.invoice_code):
                raise ValidationError(
                    _(
                        "Code combo order must consist of up to 15 uppercase letters, numbers and / symbol."
                    )
                )

    @api.constrains("session_count")
    def _check_session_count(self):
        for record in self:
            if record.session_count < 0 or record.session_count > 99999:
                raise ValidationError(
                    _("Session count must be number and max is 5 characters.")
                )

    # def create(self, value):
    #     value["is_done"] = True
    #     return super().create(value)
