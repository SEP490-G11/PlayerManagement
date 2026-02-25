# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZGynecological(models.Model):
    _name = "z_obstetric.gynecological"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Gencological examination result"

    ah = fields.Text("AH")  # AH
    ad = fields.Text("AD")  # AD
    ctc = fields.Text("CTC")  # CTC
    two_pp =  fields.Text("2PP") #2PP
    tc = fields.Text("TC")  # TC
    other = fields.Text("Other")  # Khác
    is_save = fields.Boolean("Is save", default=False, tracking=True)
    
    @api.model
    def create(self, vals):
        vals["is_save"] = True
        record = super(ZGynecological, self).create(vals)
        return record
