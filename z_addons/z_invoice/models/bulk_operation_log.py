# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class BulkOperationLog(models.Model):
    _name = "bulk.operation.log"
    _description = "Bulk Operation Log"
    _order = "create_date desc"

    name = fields.Char(string="Operation Name", required=True)
    operation_type = fields.Selection([
        ('publish', 'Bulk Publish'),
        ('email', 'Bulk Email'),
        ('cancel', 'Bulk Cancel'),
    ], string="Operation Type", required=True)
    
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, required=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, required=True)
    
    total_records = fields.Integer(string="Total Records", required=True)
    success_count = fields.Integer(string="Success Count", default=0)
    error_count = fields.Integer(string="Error Count", default=0)
    
    state = fields.Selection([
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string="Status", default='in_progress', required=True)
    
    start_time = fields.Datetime(string="Start Time", default=fields.Datetime.now, required=True)
    end_time = fields.Datetime(string="End Time")
    duration = fields.Float(string="Duration (seconds)", compute="_compute_duration", store=True)
    
    log_line_ids = fields.One2many('bulk.operation.log.line', 'log_id', string="Log Lines")
    
    # Computed fields for analytics
    success_rate = fields.Float(string="Success Rate (%)", compute="_compute_success_rate", store=True)
    avg_duration_per_record = fields.Float(string="Avg Duration per Record (s)", compute="_compute_avg_duration", store=True)
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                duration = (record.end_time - record.start_time).total_seconds()
                record.duration = duration
            else:
                record.duration = 0.0
    
    @api.depends('success_count', 'total_records')
    def _compute_success_rate(self):
        for record in self:
            if record.total_records > 0:
                record.success_rate = (record.success_count / record.total_records) * 100
            else:
                record.success_rate = 0.0
    
    @api.depends('duration', 'total_records')
    def _compute_avg_duration(self):
        for record in self:
            if record.total_records > 0:
                record.avg_duration_per_record = record.duration / record.total_records
            else:
                record.avg_duration_per_record = 0.0
    
    def action_view_log_lines(self):
        """Open log lines in a separate view"""
        return {
            'name': _('Operation Details'),
            'type': 'ir.actions.act_window',
            'res_model': 'bulk.operation.log.line',
            'view_mode': 'tree,form',
            'domain': [('log_id', '=', self.id)],
            'context': {'default_log_id': self.id},
        }
    
    def action_retry_failed_operations(self):
        """Retry failed operations based on operation type"""
        failed_lines = self.log_line_ids.filtered(lambda l: l.state == 'failed')
        if not failed_lines:
            raise ValidationError(_("No failed operations to retry"))
        
        # Get the record IDs that failed
        record_ids = failed_lines.mapped('record_id')
        
        if self.operation_type == 'publish':
            return self._retry_bulk_publish(record_ids)
        elif self.operation_type == 'email':
            return self._retry_bulk_email(record_ids)
        elif self.operation_type == 'cancel':
            return self._retry_bulk_cancel(record_ids)
    
    def _retry_bulk_publish(self, record_ids):
        """Retry bulk publish for failed records"""
        return {
            'name': _('Retry Bulk Publish'),
            'type': 'ir.actions.act_window',
            'res_model': 'bulk.publish.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_ids': [(6, 0, record_ids.ids)],
            }
        }
    
    def _retry_bulk_email(self, record_ids):
        """Retry bulk email for failed records"""
        return {
            'name': _('Retry Bulk Email'),
            'type': 'ir.actions.act_window',
            'res_model': 'bulk.email.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_ids': [(6, 0, record_ids.ids)],
            }
        }
    
    def _retry_bulk_cancel(self, record_ids):
        """Retry bulk cancel for failed records"""
        return {
            'name': _('Retry Bulk Cancel'),
            'type': 'ir.actions.act_window',
            'res_model': 'bulk.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_ids': [(6, 0, record_ids.ids)],
            }
        }


class BulkOperationLogLine(models.Model):
    _name = "bulk.operation.log.line"
    _description = "Bulk Operation Log Line"
    _order = "create_date desc"

    log_id = fields.Many2one('bulk.operation.log', string="Log", required=True, ondelete='cascade')
    record_id = fields.Many2one('account.move', string="Invoice", required=True)
    record_name = fields.Char(string="Invoice Code", related='record_id.code', readonly=True)
    
    state = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], string="Status", required=True)
    
    error_message = fields.Text(string="Error Message")
    error_details = fields.Text(string="Error Details")
    
    start_time = fields.Datetime(string="Start Time", default=fields.Datetime.now)
    end_time = fields.Datetime(string="End Time")
    duration = fields.Float(string="Duration (seconds)", compute="_compute_duration", store=True)
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                duration = (record.end_time - record.start_time).total_seconds()
                record.duration = duration
            else:
                record.duration = 0.0 