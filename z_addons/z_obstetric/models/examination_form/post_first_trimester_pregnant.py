# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZPostFirstTremesterPregnant(models.Model):
    _name = "z_obstetric.post_pregnant"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Pregnant Post-first trimester examination result" # Kết quả khám tham trên 3 tháng

    blood_pressure = fields.Text("Blood pressure")  # Huyết áp
    pulse = fields.Text("Pulse")  # Mạch
    cardiopulmonary = fields.Text("Cardiopulmonary")  # Tim phổi
    edema = fields.Text("Edema")  # Phù
    cervical_length = fields.Text("Cervical length")  # Cao tử cung
    fetal_position = fields.Text("Fetal Position")  # Ngôi
    fetal_heart = fields.Text("Fetal heart")  # Tim thai
    is_save = fields.Boolean("Is save", default=False, tracking=True)
    
    @api.model
    def create(self, vals):
        vals["is_save"] = True
        record = super(ZPostFirstTremesterPregnant, self).create(vals)
        return record
