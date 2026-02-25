# -*- coding: utf-8 -*-

from odoo import models, fields


class ExaminationCount(models.Model):
    _name = "z_ophthalmonogy.examination_count"

    prefix = fields.Char("Prefix")
    count = fields.Integer("Number examination per day")
