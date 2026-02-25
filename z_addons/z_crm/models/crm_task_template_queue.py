# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.addons.z_crm.utils.crm_utils import CRMUtils
import logging


class ZCrmTaskTemplateQueue(models.Model):
    _name = "z.crm.task.template.queue"
    _description = "CRM Task Template Queue"

    name = fields.Char(string="Template Title")
    code = fields.Char(string="Template Code")
    content = fields.Text(string="Template Content")
    execute_time = fields.Datetime(string="Execute Time")
    crm_queue_id = fields.Many2one(string="Queue", comodel_name="z.crm.queue")
    partner_id = fields.Many2one(related="crm_queue_id.partner_id")
    method = fields.Selection(related="crm_queue_id.method")
    function_name = fields.Char(string="Function Name", required=True)
    model_name = fields.Char(string="Model Name", required=False)
    count_retry= fields.Integer(string="Count Retry", default=0)
    
    status = fields.Selection(
        [("success", "Success"), ("fail", "Fail"), ("pending", "Pending")],
        string="Status",
        default="pending",
        _compute="_compute_status",
    )
    message = fields.Text(string="Message")
    
    @api.model
    def handle_task_template(self):
        now = fields.Datetime.now()
        
        if self.execute_time.date() < fields.Date.today():
                    self.status = "fail"
                    self.count_retry = 3
                    self.crm_queue_id.write({"state": "fail"})
                    self.create_log("Overdue for execution")
                    return
    
        if self.count_retry < 3:
            if self.execute_time <= now and self.status != "success"  :
                try: 
                    self.write_force({'count_retry': self.count_retry + 1})
                    function_name = self.function_name 
                    if hasattr(self, function_name):
                        method = getattr(self, function_name)
                        method() 
                        self.status = "success"
                        self.create_log("Create ticket success")
                        self.crm_queue_id.write({"state": "success"})
                    else:
                        ValidationError(f"Function '{function_name}' not exist in model '{self._name}'")
                except Exception as e:
                    if self.count_retry == 3:
                        self.status = "fail"
                        self.crm_queue_id.write({"state": "fail"})
                    else:
                        self.status = "pending"
                    self.create_log(str(e))
    
    def create_ticket_for_reexamination(self):
        self.ensure_one()
        appointment = self.env[self.crm_queue_id.model_name].browse(self.crm_queue_id.record_id)

        self.env["helpdesk.ticket"].sudo().create({
            "name": self.name,
            "partner_id": appointment.customer_id.id,
            "partner_phone": appointment.customer_id.mobile,
            "description": self.content,
            "z_ticket_type": "ab",
        })
        
    
    def create_ticket_for_glass_order(self):
        self.ensure_one()
        glass_order = self.env[self.crm_queue_id.model_name].browse(self.crm_queue_id.record_id)
        
        ticket = self.env["helpdesk.ticket"].create({
            "name": self.name,
            "partner_id": glass_order.customer_id.id,
            "partner_phone": glass_order.customer_id.mobile,
            "description": self.content,
            "z_ticket_type": "gotc",
        })        
        
    
    def create_ticket_for_care_after_exam(self):
        self.ensure_one()
        combo_order = self.env[self.crm_queue_id.model_name].browse(self.crm_queue_id.record_id)
        
        self.env["helpdesk.ticket"].create({
            "name": self.name,   
            "partner_id": combo_order.customer_id.id,
            "partner_phone": combo_order.customer_id.mobile,
            "description": self.content,
            "z_ticket_type": "gm",
        })

    
    def create_log(self, message):
         self.env['z.crm.logs'].sudo().create({
                'queue_id': self.crm_queue_id.id,
                'queue_execute_time': self.execute_time,
                'queue_status': self.status,
                'queue_logs': message,
                'template_id': self.id,
                'template_title': self.name,
            })
        
    def action_open_queue(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "z.crm.queue",
            "view_mode": "form",
            "res_id": self.crm_queue_id.id,
            "target": "new",
        }
        
    
            
