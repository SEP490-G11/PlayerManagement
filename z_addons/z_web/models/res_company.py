# -*- coding: utf-8 -*-
from odoo import models, fields


class ZResCompany(models.Model):
    _inherit = "res.company"

    code = fields.Char(string="Company Code", required=True, default="FSEC")
