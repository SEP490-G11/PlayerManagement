# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.z_invoice.helpers.misa_utils import ZMISAUtils
import logging

_logger = logging.getLogger(__name__)


class AccountMoveEmailWizard(models.TransientModel):
    _name = "account.move.email.wizard"
    _description = "Send Invoice Email Wizard"

    move_id = fields.Many2one("account.move", string="Invoice", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer", related="move_id.partner_id", readonly=True)
    customer_email = fields.Char(string="Customer Email", required=True)
    customer_name = fields.Char(string="Customer Name", related="move_id.partner_id.name", readonly=True)
    place_id = fields.Many2one("z_place.place", string="Place", related="move_id.place_id", readonly=True)
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_id'):
            move = self.env['account.move'].browse(self.env.context.get('active_id'))
            res['move_id'] = move.id
            res['customer_email'] = move.partner_id.email or ''
        return res

    def action_send_email(self):
        self.ensure_one()
        
        # Security check: Ensure user has access to the invoice
        if not self.env.user.has_group('account.group_account_invoice'):
            raise ValidationError(_("You don't have permission to send invoice emails"))
        
        # Validate email format
        if not self.customer_email:
            raise ValidationError(_("Email address is required"))
        
        # Basic email validation
        if '@' not in self.customer_email or '.' not in self.customer_email:
            raise ValidationError(_("Please enter a valid email address"))
        
        # Check if transaction ID exists
        if not self.move_id.misa_transaction_id:
            raise ValidationError(_("Transaction ID is not exist"))
        
        # Security check: Ensure user can access this specific invoice
        if not self.move_id.user_has_groups('account.group_account_invoice'):
            raise ValidationError(_("You don't have permission to access this invoice"))
        
        # Update partner email if different
        if self.customer_email != self.partner_id.email:
            self.partner_id.write({'email': self.customer_email})
        
        # Get token and send email
        token = self.place_id._get_new_token()
        
        data = {
            "SendEmailDatas": [
                {
                    "TransactionID": self.move_id.misa_transaction_id,
                    "ReceiverName": self.customer_name,
                    "ReceiverEmail": self.customer_email,
                }
            ],
            "IsInvoiceCode": True,
            "IsInvoiceCalculatingMachine": True,
        }
        
        response = ZMISAUtils.call_send_email_api(token, data, self.env)
        
        if response.get("success"):
            self.move_id.message_post(
                body=_("Email sent successfully to %s") % self.customer_email,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _("Sent VAT Invoice to customer successfully"),
                    "type": "success",
                    "sticky": False,
                    "next": {
                        "type": "ir.actions.act_window_close"
                    }
                },
            }
        else:
            _logger.error(
                f"Error sending email: {response.get('descriptionErrorCode')}"
            )
            raise ValidationError(_("Error sending email")) 