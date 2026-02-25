# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ZCombo(models.Model):
    _inherit = "z_combo.combo"
    
    sale_order_id = fields.Many2many("sale.order",)