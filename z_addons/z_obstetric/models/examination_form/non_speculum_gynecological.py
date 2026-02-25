# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZNonspeculumGynecological(models.Model):
    _name = "z_obstetric.non_gynecological"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Non Speculum Gencological examination result"

    ah = fields.Text("AH")  # AH
    hymen = fields.Text("Hymen")  # Màng trinh
    ad = fields.Text("AD")  # AD
    other = fields.Text("Other")  # Khác
    is_save = fields.Boolean("Is save", default=False, tracking=True)
    
    @api.model
    def create(self, vals):
        vals["is_save"] = True
        record = super(ZNonspeculumGynecological, self).create(vals)
        return record
