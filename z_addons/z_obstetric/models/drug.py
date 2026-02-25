# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ZDrug(models.Model):
    _inherit = ["z_medical_record.drug"]

    general_result_id = fields.Many2one(
        "z_obstetric.general_result",
        string="General result's service",
        ondelete="cascade",
    )
