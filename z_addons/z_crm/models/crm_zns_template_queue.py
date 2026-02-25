# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.addons.z_zns.helpers.utils import ZNSUltils


class ZCrmZnsTemplateQueue(models.Model):
    _name = "z.crm.zns.template.queue"
    _description = "CRM ZNS Template Queue"

    name = fields.Char(string="Template Title")
    code = fields.Char(string="Template Code")
    body = fields.Html(string="Template Body")
    execute_time = fields.Datetime(string="Execute Time")
    crm_queue_id = fields.Many2one(string="Queue", comodel_name="z.crm.queue", ondelete="cascade")
    partner_id = fields.Many2one(related="crm_queue_id.partner_id")
    method = fields.Selection(related="crm_queue_id.method")
    status = fields.Selection(
        [("success", "Success"), ("fail", "Fail"), ("pending", "Pending")],
        string="Status",
        default="pending",
    )
    number_of_run_queues = fields.Integer(string="Number of Run Queues", default=0)
    message = fields.Text(string="Message")
    msg_id = fields.Char(string="MsgID")

    def action_open_queue(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "z.crm.queue",
            "view_mode": "form",
            "res_id": self.crm_queue_id.id,
            "target": "new",
        }

    number_run_cron = fields.Integer(string="Number Run Cron", default=0)

    @api.model
    def handle_zns_template(self):
        function_name = self.code
        model_name = self.crm_queue_id.model_name
        record_id = self.crm_queue_id.record_id
        crm_queue_id = self.crm_queue_id.id

        # Check overdue
        if self.execute_time.date() != fields.Date.today():
            self._update_status(
                crm_queue_id, 
                status="fail", 
                message="Overdue for execution", 
                msg_id=False, 
                number_of_run_queues=3
            )
            return "fail"

        data_zns = self.env[model_name].search([("id", "=", record_id)])
        if not hasattr(ZNSUltils, function_name) or not data_zns:
            return False

        # run action 
        method = getattr(ZNSUltils, function_name)
        status, message, msg_id = method(self, data_zns)

        # Update crm queue and save log
        self._update_status(
            crm_queue_id, 
            status="success" if status else "fail", 
            message=message if not status else "Success", 
            msg_id=msg_id if status else False, 
            number_of_run_queues=self.number_of_run_queues + 1
        )
        return status

    def _update_status(self, crm_queue_id, status, message, msg_id, number_of_run_queues):
        """Update queue"""
        for rec in self:
            rec.message = message
            rec.status = status
            rec.msg_id = msg_id
            rec.number_of_run_queues = number_of_run_queues

        # Save log
        self.env["z.crm.logs"].sudo().create(
            {
                "queue_id": crm_queue_id,
                "queue_execute_time": self.execute_time,
                "queue_status": status,
                "queue_logs": message,
                "template_id": self.id,
                "template_title": self.name,
            }
        )
