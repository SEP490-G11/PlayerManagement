# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ZCrmZnsTemplate(models.Model):
    _name = "z.crm.zns.template"
    _description = "CRM ZNS Template"

    name = fields.Char(string="Template Title")
    code = fields.Char(string="Template Code")
    body = fields.Html(string="Template Body")
    crm_queue_id = fields.Many2one(string="Queue", comodel_name="z.crm.queue")
