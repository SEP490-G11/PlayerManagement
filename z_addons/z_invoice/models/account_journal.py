# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, exceptions, _


class ZAccountMove(models.Model):
    _inherit = "account.journal"

    place_id = fields.Many2one("z_place.place", string="Place")