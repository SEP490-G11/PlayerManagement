# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZFullBody(models.Model):
    _name = "z_obstetric.full_body"
    _inherit = ["z_medical_record.medical_result"]
    
    perception = fields.Text("Perception")  # Tri giác
    blood_pressure = fields.Text("Blood pressure")  # Huyết áp/mạch
    physical_condition = fields.Text("Physical condition")  # Thể trạng
    skin_mucous_membrane = fields.Text("Skin, mucous membrane")  # Da, niêm mạc 
    is_save = fields.Boolean("Is save", default=False, tracking=True)
    
    @api.model
    def create(self, vals):
        vals["is_save"] = True
        record = super(ZFullBody, self).create(vals)
        return record
