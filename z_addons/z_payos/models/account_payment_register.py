from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from payos import PayOS, ItemData, PaymentData
import time


class ZAccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    viet_qr_reconcile_code = fields.Many2one(
        "z_payos.qr.logs",
        string="QR Reconcile Code",
        store=True,
        domain="[('move_id', '=', move_id),('payment_status','=','Paid'),('is_create_account_payment','=',False)]",
    )
    is_payos_payment = fields.Boolean(string="Is PayOS Payment", default=False)
    viet_qr_amount = fields.Float(string="Viet QR Amount", default=0.0)
    invoice_code = fields.Char(string="Invoice Code", readonly=True)
    move_id = fields.Many2one("account.move", string="Move ID", readonly=True)

    @api.model
    def default_get(self, fields_list):
        # OVERRIDE
        res = super().default_get(fields_list)
        ticket = self.env[self._context.get("active_model")].browse(
            self._context.get("active_ids")
        )
        code = ticket.mapped("move_id").code
        res["invoice_code"] = code
        move_id = (
            self.env["account.move.line"]
            .browse(self._context.get("active_ids", []))
            .mapped("move_id")
        )
        res["move_id"] = move_id.id
        if "line_ids" in fields_list and "line_ids" not in res:

            # Retrieve moves to pay from the context.

            if self._context.get("active_model") == "account.move":
                lines = (
                    self.env["account.move"]
                    .browse(self._context.get("active_ids", []))
                    .line_ids
                )
            elif self._context.get("active_model") == " account.move.line":
                lines = self.env["account.move.line"].browse(
                    self._context.get("active_ids", [])
                )
                raise UserError(
                    _(
                        "The register payment wizard should only be called on account.move or account.move.line records."
                    )
                )

            if "journal_id" in res and not self.env["account.journal"].browse(
                res["journal_id"]
            ).filtered_domain(
                [
                    *self.env["account.journal"]._check_company_domain(
                        lines.company_id
                    ),
                    ("type", "in", ("bank", "cash")),
                ]
            ):
                # default can be inherited from the list view, should be computed instead
                del res["journal_id"]

            # Keep lines having a residual amount to pay.
            available_lines = self.env["account.move.line"]
            valid_account_types = self.env[
                "account.payment"
            ]._get_valid_payment_account_types()
            for line in lines:
                if line.move_id.state != "posted":
                    raise UserError(
                        _("You can only register payment for posted journal entries.")
                    )

                if line.account_type not in valid_account_types:
                    continue
                if line.currency_id:
                    if line.currency_id.is_zero(line.amount_residual_currency):
                        continue
                else:
                    if line.company_currency_id.is_zero(line.amount_residual):
                        continue
                available_lines |= line

            # Check.
            if not available_lines:
                raise UserError(
                    _(
                        "You can't register a payment because there is nothing left to pay on the selected journal items."
                    )
                )
            if len(lines.company_id.root_id) > 1:
                raise UserError(
                    _(
                        "You can't create payments for entries belonging to different companies."
                    )
                )
            if len(set(available_lines.mapped("account_type"))) > 1:
                raise UserError(
                    _(
                        "You can't register payments for both inbound and outbound moves at the same time."
                    )
                )

            res["line_ids"] = [(6, 0, available_lines.ids)]
        if self._context.get("is_qr_payment"):
            res["is_payos_payment"] = self._context.get("is_qr_payment")
            amount = self._context.get("amount")
            qr_log_id = self._context.get("qr_log_id") or None
            res["amount"] = amount
            res["viet_qr_reconcile_code"] = qr_log_id
        return res

    @api.depends(
        "can_edit_wizard",
        "source_amount",
        "source_amount_currency",
        "source_currency_id",
        "company_id",
        "currency_id",
        "payment_date",
        "viet_qr_reconcile_code",
    )
    def _compute_amount(self):
        for wizard in self:
            if self.viet_qr_reconcile_code:
                wizard.amount = wizard.viet_qr_reconcile_code.payment_amount
            elif (
                not wizard.journal_id
                or not wizard.currency_id
                or not wizard.payment_date
            ):
                wizard.amount = wizard.amount
            elif wizard.source_currency_id and wizard.can_edit_wizard:
                batch_result = wizard._get_batches()[0]
                wizard.amount = (
                    wizard._get_total_amount_in_wizard_currency_to_full_reconcile(
                        batch_result
                    )[0]
                )
            else:
                # The wizard is not editable so no partial payment allowed and
                # then, 'amount' is not used.
                wizard.amount = None

    @api.depends("available_journal_ids", "viet_qr_reconcile_code")
    def _compute_journal_id(self):
        for wizard in self:
            if wizard.viet_qr_reconcile_code:
                bank = self.env["res.partner.bank"].search(
                    [("acc_number", "=", wizard.viet_qr_reconcile_code.account_bank)],
                    limit=1,
                )
                if bank.id:
                    wizard.journal_id = self.env["account.journal"].search(
                        [
                            *self.env["account.journal"]._check_company_domain(
                                wizard.company_id
                            ),
                            ("bank_account_id", "=", bank.id),
                        ],
                        limit=1,
                    )
            elif wizard.can_edit_wizard:
                batch = wizard._get_batches()[0]
                wizard.journal_id = wizard._get_batch_journal(batch)
            else:
                wizard.journal_id = self.env["account.journal"].search(
                    [
                        *self.env["account.journal"]._check_company_domain(
                            wizard.company_id
                        ),
                        ("type", "in", ("bank", "cash")),
                        ("id", "in", self.available_journal_ids.ids),
                    ],
                    limit=1,
                )

    def create(self, values):
        if self._context.get("qr_log_id"):
            qr_log = self.env["z_payos.qr.logs"].search(
                [("id", "=", self._context.get("qr_log_id"))]
            )
            qr_log.write({"is_create_account_payment": True})

        return super().create(values)

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        payment_vals.update(
            {
                "viet_qr_transaction_id": self.viet_qr_reconcile_code.id,
            }
        )
        return payment_vals
