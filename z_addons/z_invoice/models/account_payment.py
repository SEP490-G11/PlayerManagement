# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ZAccountPayment(models.Model):
    _inherit = "account.payment"
    reconciled_invoice_code = fields.Char(
        string="Reconciled Invoice Code",
        compute="_compute_reconciled_invoice",
        store=True,
    )
    reconciled_invoice_total_signed = fields.Float(
        compute="_compute_reconciled_invoice", digits="Invoice"
    )
    reconciled_invoice_paid = fields.Float(
        compute="_compute_reconciled_invoice", digits="Invoice"
    )
    reconciled_invoice_total_discount = fields.Float(
        compute="_compute_reconciled_invoice", digits="Invoice"
    )

    # Smart button field to count invoices with amount greater than payment amount
    invoice_count = fields.Integer(
        string="Invoice Count",
        compute="_compute_invoice_count",
        help="Number of invoices with total amount greater than payment amount"
    )

    amount = fields.Monetary(currency_field="currency_id", digits=(12, 0))
    journal_name = fields.Char(
        string="Journal Name", related="journal_id.name", store=True
    )

    computed_name = fields.Char(
        compute="_compute_computed_fields", store=True, string="Computed Name"
    )
    computed_date = fields.Date(
        compute="_compute_computed_fields", store=True, string="Computed Date"
    )
    is_prepayment = fields.Boolean(string="Prepayment", default=False)

    explanation = fields.Text(string="Explanation", tracking=True)
    
    place_id = fields.Many2one("z_place.place", string="Place" )

    @api.depends("display_name", "date")
    def _compute_computed_fields(self):
        for record in self:
            record.computed_name = record.display_name or False
            record.computed_date = record.date or False

    @api.depends("partner_id", "amount", "currency_id")
    def _compute_invoice_count(self):
        """Compute the count of invoices with total amount greater than payment amount"""
        for record in self:
            if record.partner_id and record.amount:
                # Search for invoices of this customer with amount_total > payment amount
                domain = [
                    ('partner_id', '=', record.partner_id.id),
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('amount_total', '>', record.amount),
                ]
                record.invoice_count = self.env['account.move'].search_count(domain)
            else:
                record.invoice_count = 0

    def action_view_invoices(self):
        """Open the list view of invoices with amount greater than payment amount"""
        self.ensure_one()
        
        if not self.partner_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('No customer selected for this payment.'),
                }
            }

        # Search for invoices with amount_total > payment amount
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('amount_total', '>', self.amount),
        ]
        
        invoices = self.env['account.move'].search(domain)
        
        if not invoices:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'info',
                    'message': _('No invoices found with amount greater than payment amount (%s).') % self.amount,
                }
            }

        return {
            'name': _('Can be paid'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_move_type': 'out_invoice',
            },
            'target': 'current',
            'order': 'date desc, id desc',
        }

    
    def action_print_payment_slip(self):
        action = self.env["ir.actions.report"]._for_xml_id(
            "z_invoice.action_report_account_payment_document"
        )
        return action
    
    @api.depends("reconciled_invoice_ids")
    def _compute_reconciled_invoice(self):
        for record in self:
            reconciled_invoice = record.reconciled_invoice_ids[:1]
            if reconciled_invoice:
                record.reconciled_invoice_code = reconciled_invoice.code
                record.reconciled_invoice_total_signed = (
                    reconciled_invoice.amount_total_signed
                )
                record.reconciled_invoice_paid = reconciled_invoice.paid
                record.reconciled_invoice_total_discount = (
                    reconciled_invoice.total_discount
                )
            else:
                record.reconciled_invoice_code = ""
                record.reconciled_invoice_total_signed = 0
                record.reconciled_invoice_paid = 0
                record.reconciled_invoice_total_discount = 0
    
    @api.onchange("journal_id")
    def _onchange_journal_id(self):
        for record in self:
            if record.journal_id.place_id:
                record.place_id = record.journal_id.place_id

    @api.constrains("date")
    def _check_past_date(self):
        for record in self:
            if record.date > fields.Date.today():
                raise ValidationError(_("Payment slip cannot be made in the future"))
