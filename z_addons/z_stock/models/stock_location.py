# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ZStockLocation(models.Model):
    _inherit = "stock.location"

    place_id = fields.Many2one(
        "z_place.place",
        string="Cơ sở",
        related="warehouse_id.place_id",
    )
