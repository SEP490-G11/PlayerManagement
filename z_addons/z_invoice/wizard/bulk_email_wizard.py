# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.z_invoice.helpers.misa_utils import ZMISAUtils
import logging

_logger = logging.getLogger(__name__)


class BulkEmailWizard(models.TransientModel):
    _name = "bulk.email.wizard"
    _description = "Bulk Send Email Wizard"

    move_ids = fields.Many2many("account.move", string="Invoices to Send Email", required=True)
    count = fields.Integer(string="Number of Invoices", readonly=True, compute="_compute_count", store=True)
    customer_email = fields.Char(string="Customer Email", required=True)
    progress = fields.Float(string="Progress", default=0.0, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('done', 'Done')
    ], default='draft', string="State")
    

    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Get move_ids from context
        move_ids = self.env.context.get('default_move_ids') or self.env.context.get('active_ids', [])
        if move_ids:
            if isinstance(move_ids[0], tuple):
                # Handle [(6, 0, ids)] format
                moves = self.env['account.move'].browse(move_ids[0][2])
            else:
                # Handle direct ids list
                moves = self.env['account.move'].browse(move_ids)
            
            # Get the most common email from the moves
            emails = moves.mapped('partner_id.email')
            if emails:
                res['customer_email'] = emails[0]
            # Set count
            res['count'] = len(moves)
        return res

    def action_confirm_send_email(self):
        self.ensure_one()
        
        if not self.customer_email:
            raise ValidationError(_("Please enter customer email"))
        
        # Basic email validation
        if '@' not in self.customer_email or '.' not in self.customer_email:
            raise ValidationError(_("Please enter a valid email address"))
        
        # Validate all invoices can send email
        invalid_moves = self.move_ids.filtered(
            lambda m: m.misa_state != 'published' or not m.misa_transaction_id
        )
        if invalid_moves:
            raise ValidationError(_("Some invoices cannot send email: %s") % ', '.join(invalid_moves.mapped('code')))
        
        # Create bulk operation log
        log = self.env['bulk.operation.log'].create({
            'name': _('Bulk Email - %s') % fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation_type': 'email',
            'total_records': len(self.move_ids),
            'state': 'in_progress',
        })
        
        self.state = 'processing'
        
        # Process each invoice
        success_count = 0
        error_count = 0
        
        for i, move in enumerate(self.move_ids):
            log_line = self.env['bulk.operation.log.line'].create({
                'log_id': log.id,
                'record_id': move.id,
                'state': 'failed',  # Default to failed, will be updated on success
                'start_time': fields.Datetime.now(),
            })
            
            try:
                # Update progress and force UI refresh
                self.progress = (i + 1) / len(self.move_ids) * 100
                self.env.cr.commit()  # Force database commit to update UI
                
                # Update partner email if different
                if self.customer_email != move.partner_id.email:
                    move.partner_id.write({'email': self.customer_email})
                
                # Get token and send email
                token = move.place_id._get_new_token()
                
                data = {
                    "SendEmailDatas": [
                        {
                            "TransactionID": move.misa_transaction_id,
                            "ReceiverName": move.partner_id.name,
                            "ReceiverEmail": self.customer_email,
                        }
                    ],
                    "IsInvoiceCode": True,
                    "IsInvoiceCalculatingMachine": True,
                }
                
                response = ZMISAUtils.call_send_email_api(token, data, self.env)
                
                if response.get("success"):
                    move.message_post(
                        body=_("Email sent successfully to %s") % self.customer_email,
                    )
                    success_count += 1
                    log_line.write({
                        'state': 'success',
                        'end_time': fields.Datetime.now(),
                    })
                else:
                    error_count += 1
                    error_msg = response.get('descriptionErrorCode', 'Unknown error')
                    log_line.write({
                        'error_message': error_msg,
                        'error_details': _('MISA API returned error response'),
                        'end_time': fields.Datetime.now(),
                    })
                    _logger.error(f"Error sending email for invoice {move.code}: {error_msg}")
                    
            except Exception as e:
                error_count += 1
                log_line.write({
                    'error_message': str(e),
                    'error_details': _('Exception occurred during email sending'),
                    'end_time': fields.Datetime.now(),
                })
                _logger.error(f"Error sending email for invoice {move.code}: {str(e)}")
        
        # Update log with final results
        log.write({
            'success_count': success_count,
            'error_count': error_count,
            'state': 'completed' if error_count == 0 else 'failed',
            'end_time': fields.Datetime.now(),
        })
        
        self.state = 'done'
        
        # Show results with log link
        message = _("Email sending completed!\n\n")
        message += _("✅ Successfully sent: %d emails\n") % success_count
        if error_count > 0:
            message += _("❌ Failed to send: %d emails\n\n") % error_count
            message += _("Check the bulk operation logs for detailed error information.")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Email Results'),
                'message': message,
                'type': 'success' if error_count == 0 else 'warning',
                'sticky': True,
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'bulk.operation.log',
                    'res_id': log.id,
                    'view_mode': 'form',
                    'target': 'current',
                }
            }
        } 