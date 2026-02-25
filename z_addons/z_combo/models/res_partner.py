# -*- coding: utf-8 -*-
from odoo import fields, models


class ZPartner(models.Model):
    _inherit = "res.partner"
    
    purchased_combo_line_ids = fields.One2many('z_combo.purchased.combo.line', 'partner_id', string='Purchased Combo Lines')