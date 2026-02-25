# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class BulkCancelWizard(models.TransientModel):
    _name = "bulk.cancel.wizard"
    _description = "Bulk Cancel Invoices Wizard"

    move_ids = fields.Many2many("account.move", string="Invoices to Cancel", required=True)
    count = fields.Integer(string="Number of Invoices", readonly=True, compute="_compute_count", store=True)
    confirm_cancel = fields.Boolean(string="I confirm I want to cancel these invoices", default=False)
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
            
            # Set count
            res['count'] = len(moves)
        return res

    def action_confirm_cancel(self):
        self.ensure_one()
        
        if not self.confirm_cancel:
            raise ValidationError(_("Please confirm that you want to cancel these invoices"))
        
        # Validate all invoices can be cancelled
        invalid_moves = self.move_ids.filtered(
            lambda m: m.state != 'draft' or m.misa_state == 'published'
        )
        if invalid_moves:
            raise ValidationError(_("Some invoices cannot be cancelled: %s") % ', '.join(invalid_moves.mapped('code')))
        
        # Create bulk operation log
        log = self.env['bulk.operation.log'].create({
            'name': _('Bulk Cancel - %s') % fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation_type': 'cancel',
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
                
                # Cancel the invoice
                move.button_cancel()
                success_count += 1
                log_line.write({
                    'state': 'success',
                    'end_time': fields.Datetime.now(),
                })
                    
            except Exception as e:
                error_count += 1
                log_line.write({
                    'error_message': str(e),
                    'error_details': _('Exception occurred during cancellation'),
                    'end_time': fields.Datetime.now(),
                })
                _logger.error(f"Error cancelling invoice {move.code}: {str(e)}")
        
        # Update log with final results
        log.write({
            'success_count': success_count,
            'error_count': error_count,
            'state': 'completed' if error_count == 0 else 'failed',
            'end_time': fields.Datetime.now(),
        })
        
        self.state = 'done'
        
        # Show results with log link
        message = _("Cancellation completed!\n\n")
        message += _("✅ Successfully cancelled: %d invoices\n") % success_count
        if error_count > 0:
            message += _("❌ Failed to cancel: %d invoices\n\n") % error_count
            message += _("Check the bulk operation logs for detailed error information.")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Cancel Results'),
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