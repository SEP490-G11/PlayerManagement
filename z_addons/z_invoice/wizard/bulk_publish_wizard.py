# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class BulkPublishWizard(models.TransientModel):
    _name = "bulk.publish.wizard"
    _description = "Bulk Publish Invoices Wizard"

    move_ids = fields.Many2many("account.move", string="Invoices to Publish", required=True)
    count = fields.Integer(string="Number of Invoices", readonly=True)
    misa_template_id = fields.Many2one(
        "z_invoice.misa_invoice_template", 
        string="MISA Template", 
        required=True
    )
    place_ids = fields.Many2many("z_place.place", string="Places", compute="_compute_place_ids")
    progress = fields.Float(string="Progress", default=0.0, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('done', 'Done')
    ], default='draft', string="State")
    
    @api.depends('move_ids')
    def _compute_place_ids(self):
        for record in self:
            record.place_ids = record.move_ids.mapped('place_id')
    

    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('default_move_ids'):
            moves = self.env['account.move'].browse(self.env.context.get('default_move_ids')[0][2])
            # Get the most common template from the moves
            templates = moves.mapped('misa_template_id')
            if templates:
                res['misa_template_id'] = templates[0].id
            # Set count
            res['count'] = len(moves)
        return res

    def action_confirm_publish(self):
        self.ensure_one()
        
        # Sort move_ids by invoice_date from past to present (ascending order)
        sorted_moves = self.move_ids.sorted('invoice_date')
        
        # If no template is selected, try to get one from the moves
        if not self.misa_template_id:
            templates = sorted_moves.mapped('misa_template_id')
            if templates:
                self.misa_template_id = templates[0]
            else:
                raise ValidationError(_("Please select a MISA template or ensure invoices have templates assigned"))
        
        # Validate all invoices can be published
        today = fields.Date.today()
        invalid_moves = sorted_moves.filtered(
            lambda m: m.state != 'posted' or m.misa_state != 'draft' or m.move_type not in ('out_invoice', 'out_refund') or m.invoice_date != today
        )
        if invalid_moves:
            invalid_reasons = []
            for move in invalid_moves:
                if move.state != 'posted':
                    invalid_reasons.append(f"{move.code}: Not posted")
                elif move.misa_state != 'draft':
                    invalid_reasons.append(f"{move.code}: Already published")
                elif move.move_type not in ('out_invoice', 'out_refund'):
                    invalid_reasons.append(f"{move.code}: Invalid move type")
                elif move.invoice_date != today:
                    invalid_reasons.append(f"{move.code}: Invoice date is not today.")
            
            raise ValidationError(_("Some invoices cannot be published:\n%s") % '\n'.join(invalid_reasons))
        
        # Create bulk operation log
        log = self.env['bulk.operation.log'].create({
            'name': _('Bulk Publish - %s') % fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation_type': 'publish',
            'total_records': len(sorted_moves),
            'state': 'in_progress',
        })
        
        self.state = 'processing'
        
        # Process each invoice
        success_count = 0
        error_count = 0
        
        for i, move in enumerate(sorted_moves):
            log_line = self.env['bulk.operation.log.line'].create({
                'log_id': log.id,
                'record_id': move.id,
                'state': 'failed',  # Default to failed, will be updated on success
                'start_time': fields.Datetime.now(),
            })
            
            try:
                # Update progress and force UI refresh
                self.progress = (i + 1) / len(sorted_moves) * 100
                self.env.cr.commit()  # Force database commit to update UI
                
                # Set template if not set
                if not move.misa_template_id:
                    move.misa_template_id = self.misa_template_id
                
                # Publish the invoice
                wizard = self.env['account.move.misa.issuance'].create({
                    'move_id': move.id,
                    'misa_template_id': self.misa_template_id.id,
                })
                
                result = wizard.action_publish()
                if result and result.get('type') == 'ir.actions.client':
                    success_count += 1
                    log_line.write({
                        'state': 'success',
                        'end_time': fields.Datetime.now(),
                    })
                else:
                    error_count += 1
                    log_line.write({
                        'error_message': _('Unexpected result from publish operation'),
                        'end_time': fields.Datetime.now(),
                    })
                    _logger.error(f"Error publishing invoice {move.code}: Unexpected result")
                    
            except Exception as e:
                error_count += 1
                log_line.write({
                    'error_message': str(e),
                    'error_details': _('Exception occurred during publish operation'),
                    'end_time': fields.Datetime.now(),
                })
                _logger.error(f"Error publishing invoice {move.code}: {str(e)}")
        
        # Update log with final results
        log.write({
            'success_count': success_count,
            'error_count': error_count,
            'state': 'completed' if error_count == 0 else 'failed',
            'end_time': fields.Datetime.now(),
        })
        
        self.state = 'done'
        
        # Show results with log link
        message = _("Publishing completed!\n\n")
        message += _("Successfully published: %d invoices\n") % success_count
        if error_count > 0:
            message += _("Failed to publish: %d invoices\n\n") % error_count
            message += _("Check the bulk operation logs for detailed error information.")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Publish Results'),
                'message': message,
                'type': 'success' if error_count == 0 else 'warning',
                'sticky': True,
                'next': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }