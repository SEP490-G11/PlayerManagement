# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ZCrmLogs(models.Model):
    _name = "z.crm.logs"
    _description = "CRM Logs"

    queue_id  = fields.Integer(string="Queue")
    queue_execute_time = fields.Datetime(
        string="Queue Execute Time"
    )
    queue_status = fields.Boolean(string="Queue Status")
    queue_logs = fields.Text(string="Queue Logs")
    template_id = fields.Integer(string="Template id")
    template_title = fields.Text(string="Template title")

