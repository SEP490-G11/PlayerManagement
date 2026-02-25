# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ZDrug(models.Model):
    _inherit = ["z_medical_record.drug"]

    comprehensive_id = fields.Many2one(
        "z_ophthalmology.comprehensive",
        string="Comprehensive examination result's drug",
        ondelete="cascade",
    )
    lens_id = fields.Many2one(
        "z_ophthalmology.lens",
        string="Lens examination result's drug",
        ondelete="cascade",
    )
    re_lens_id = fields.Many2one(
        "z_ophthalmology.re_lens",
        string="Lens reexamination result's drug",
        ondelete="cascade",
    )
    vision_id = fields.Many2one(
        "z_ophthalmology.vision",
        string="Low vision examination result's drug",
        ondelete="cascade",
    )
    binocular_vision_id = fields.Many2one(
        "z_ophthalmology.binocular_vision",
        string="Binocular vision examination result's drug",
        ondelete="cascade",
    )
