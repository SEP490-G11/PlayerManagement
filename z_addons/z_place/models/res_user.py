# -*- coding: utf-8 -*-

from odoo import fields, models, _

class ResUsers(models.Model):
    _inherit = "res.users"
    place_ids = fields.Many2many("z_place.place", string="Places", tracking=True)