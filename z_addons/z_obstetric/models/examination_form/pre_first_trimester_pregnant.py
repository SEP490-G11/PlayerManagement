# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZPreFirstTremesterPregnant(models.Model):
    _name = "z_obstetric.pre_pregnant"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Pregnant Pre-first trimester examination result" # Kết quả khám tham dưới 3 tháng

    blood_pressure = fields.Text("Blood pressure")  # Huyết áp
    cardiopulmonary = fields.Text("Cardiopulmonary")  # Tim phổi
    fetal_heart = fields.Text("Fetal heart")  # Tim thai
    pulse = fields.Text("Pulse")  # Mạch
    is_save = fields.Boolean("Is save", default=False, tracking=True)
    
    @api.model
    def create(self, vals):
        vals["is_save"] = True
        record = super(ZPreFirstTremesterPregnant, self).create(vals)
        return record
