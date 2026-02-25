# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import logging

_logger = logging.getLogger(__name__)

class MisaLog(models.Model):
    _name = "z_invoice.misa_log"
    _description = "MISA Invoice Publishing Log"
    _order = "create_date desc"

    # Basic Information
    invoice_id = fields.Many2one(
        "account.move", 
        string="Invoice", 
        required=True, 
        ondelete="cascade"
    )
    
    # MISA Information
    misa_template_id = fields.Many2one(
        "z_invoice.misa_invoice_template",
        string="MISA Template",
        required=True
    )
    
    status = fields.Selection([
        ('pending', _('Pending')),
        ('success', _('Success')),
        ('failed', _('Failed')),
    ], string="Status", required=True, default="pending")
    
    # Error Information
    error_message = fields.Text(string="Error Message")
    error_code = fields.Char(string="Error Code")
    error_details = fields.Text(string="Error Details")
    
    # Timing Information
    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")
    duration_seconds = fields.Float(string="Duration (seconds)", compute="_compute_duration")
    
    # User Information
    user_id = fields.Many2one(
        "res.users", 
        string="Processed By", 
        default=lambda self: self.env.user.id,
        required=True
    )
    
    # Additional Information
    notes = fields.Text(string="Notes")
    retry_count = fields.Integer(string="Retry Count", default=0)
    max_retries = fields.Integer(string="Max Retries", default=3)
    
    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                duration = (record.end_time - record.start_time).total_seconds()
                record.duration_seconds = duration
            else:
                record.duration_seconds = 0.0
    
    def log_request_start(self, invoice_id, template_id, operation_type="publish"):
        """Log the start of a MISA operation"""
        return self.create({
            'invoice_id': invoice_id,
            'misa_template_id': template_id,
            'status': 'pending',
            'start_time': fields.Datetime.now(),
            'user_id': self.env.user.id,
        })
    
    def log_request_success(self, transaction_id=None, inv_no=None, inv_code=None, url=None, response_data=None):
        """Log successful completion of a MISA operation"""
        self.ensure_one()
        self.write({
            'status': 'success',
            'misa_transaction_id': transaction_id,
            'misa_inv_no': inv_no,
            'misa_inv_code': inv_code,
            'misa_url': url,
            'response_data': json.dumps(response_data) if response_data else None,
            'end_time': fields.Datetime.now(),
        })
    
    def log_request_failure(self, error_message, error_code=None, error_details=None, request_data=None):
        """Log failed MISA operation"""
        self.ensure_one()
        self.write({
            'status': 'failed',
            'error_message': error_message,
            'error_code': error_code,
            'error_details': error_details,
            'request_data': json.dumps(request_data) if request_data else None,
            'end_time': fields.Datetime.now(),
        })
    
    def log_request_cancelled(self, reason=None):
        """Log cancelled MISA operation"""
        self.ensure_one()
        self.write({
            'status': 'cancelled',
            'error_message': reason or _("Operation cancelled"),
            'end_time': fields.Datetime.now(),
        })
    
    def increment_retry_count(self):
        """Increment retry count for failed operations"""
        self.ensure_one()
        self.retry_count += 1
    
    def can_retry(self):
        """Check if operation can be retried"""
        return self.status == 'failed' and self.retry_count < self.max_retries
    
    def get_logs_for_invoice(self, invoice_id):
        """Get all logs for a specific invoice"""
        return self.search([('invoice_id', '=', invoice_id)], order='create_date desc')
    
    def get_failed_logs(self, days=7):
        """Get failed logs from the last N days"""
        from datetime import datetime, timedelta
        date_limit = datetime.now() - timedelta(days=days)
        return self.search([
            ('status', '=', 'failed'),
            ('create_date', '>=', date_limit)
        ], order='create_date desc')
    
    def get_success_rate(self, days=30):
        """Calculate success rate for the last N days"""
        from datetime import datetime, timedelta
        date_limit = datetime.now() - timedelta(days=days)
        logs = self.search([('create_date', '>=', date_limit)])
        
        if not logs:
            return 0.0
        
        success_count = len(logs.filtered(lambda l: l.status == 'success'))
        return (success_count / len(logs)) * 100
    
    def cleanup_old_logs(self, days=90):
        """Clean up logs older than N days"""
        from datetime import datetime, timedelta
        date_limit = datetime.now() - timedelta(days=days)
        old_logs = self.search([('create_date', '<', date_limit)])
        
        count = len(old_logs)
        old_logs.unlink()
        _logger.info(f"Cleaned up {count} old MISA logs older than {days} days")
        return count
    
    def action_retry(self):
        """Retry failed MISA operation"""
        self.ensure_one()
        
        if not self.can_retry():
            raise ValidationError(_("This operation cannot be retried"))
        
        # Create new log entry for retry
        new_log = self.create({
            'invoice_id': self.invoice_id.id,
            'misa_template_id': self.misa_template_id.id,
            'operation_type': self.operation_type,
            'status': 'pending',
            'start_time': fields.Datetime.now(),
            'user_id': self.env.user.id,
            'notes': f"Retry attempt {self.retry_count + 1} for log ID {self.id}",
        })
        
        # Try to execute the operation
        try:
            if self.operation_type == 'publish':
                # Create wizard and retry publish
                wizard = self.env['account.move.misa.issuance'].create({
                    'move_id': self.invoice_id.id,
                    'misa_template_id': self.misa_template_id.id,
                })
                result = wizard.action_publish()
                
                if result and result.get('type') == 'ir.actions.client':
                    new_log.log_request_success(
                        transaction_id=self.misa_transaction_id,
                        inv_no=self.misa_inv_no,
                        inv_code=self.misa_inv_code,
                        url=self.misa_url
                    )
                else:
                    new_log.log_request_failure("Retry failed - unexpected result")
                    
            else:
                new_log.log_request_failure("Retry not implemented for this operation type")
                
        except Exception as e:
            new_log.log_request_failure(str(e))
            raise ValidationError(_("Retry failed: %s") % str(e))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('MISA Log'),
            'res_model': 'z_invoice.misa_log',
            'res_id': new_log.id,
            'view_mode': 'form',
            'target': 'current',
        } 