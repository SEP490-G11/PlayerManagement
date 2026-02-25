# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ZCrmTaskTemplate(models.Model):
    _name = "z.crm.task.template"
    _description = "CRM Task Template"

    name = fields.Char(string="Template Title")
    code = fields.Char(string="Template Code")
    content = fields.Text(string="Template Content")
    crm_queue_id = fields.Many2one(string="Queue", comodel_name="z.crm.queue")
    
    

    
    
    
    
    
    
    
