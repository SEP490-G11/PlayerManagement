from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from datetime import date, datetime


class ZQRLogs(models.Model):
    _name = "z_payos.qr.logs"
    _rec_name = "payment_description"

    payment_channel = fields.Char(
        string="Payment Channel",
        default="PayOS",
    )
    payment_amount = fields.Float(
        string="Payment Amount",
        default=0.0,
        digits=(12, 0),
    )
    invoice_amount = fields.Float(
        string="Invoice Amount",
        default=0.0,
        digits=(12, 0),
    )
    payment_description = fields.Char(
        string="Payment Description", default="Payment for invoice"
    )
    account_bank = fields.Char(string="Account Bank")
    bin = fields.Char(string="Bin")
    payment_code = fields.Char(string="Payment Code")
    payment_status = fields.Selection(
        [
            ("Pending", "Pending"),
            ("Paid", "Paid"),
            ("Failed", "Failed"),
            ("Canceled", "Canceled"),
        ],
        string="Payment Status",
        default="Pending",
    )
    is_create_account_payment = fields.Boolean(
        string="Create Account Payment", default=False
    )
    move_id = fields.Many2one(
        "account.move", string="Account Move", ondelete="cascade"
    )
    payment_id = fields.Many2one(
        "account.payment", string="Account Payment", ondelete="cascade"
    )
    can_create_account_payment = fields.Boolean(
        string="Can Create Account Payment", compute="_compute_can_create_account_payment"
    )
    
    place = fields.Char(string="Place")
    
    payment_register =  fields.One2many(
        "account.payment.register", "viet_qr_reconcile_code", string="Payment Register")

    can_create_account_payment = fields.Boolean(
        string="Can Create Account Payment",
        compute="_compute_can_create_account_payment",
    )

    payment_register = fields.One2many(
        "account.payment.register", "viet_qr_reconcile_code", string="Payment Register"
    )

    @api.depends("payment_status", "is_create_account_payment")
    def _compute_can_create_account_payment(self):
        for record in self:
            record.can_create_account_payment = (
                record.payment_status == "Paid" and not record.is_create_account_payment
            )

    def cancel_qr_payment(self):
        current_user = self.env.user
        channel = f"notification.counter_{current_user.id}"
        self.env["bus.bus"]._sendone(
            channel,
            "notification.counter/cancel_qr_event",
            {},
        )
        if self.payment_status == "Paid":
            raise ValidationError(_("Payment has already been paid"))
        self.payment_status = "Canceled"

    def pay_qr_payment(self):
        if self.payment_status == "Paid":
            raise ValidationError(_("Payment has already been paid"))
        self.payment_status = "Paid"

    def open_create_account_payment_wizard(self):
        self.ensure_one()
        if not self.can_create_account_payment:
            raise ValidationError(_("Cannot create account payment"))

        self.move_id.action_register_payment_with_qr()
