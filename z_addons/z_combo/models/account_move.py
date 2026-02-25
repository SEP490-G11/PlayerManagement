# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from datetime import date


class ZAccountMove(models.Model):
    _inherit = "account.move"

    combo_line_ids = fields.Many2many("z_combo.combo", "Combo")


class ZAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    combo_id = fields.Many2one("z_combo.combo", "Combo")
    sub_combo_id = fields.Many2one("z_combo.combo", "Sub Combo")
