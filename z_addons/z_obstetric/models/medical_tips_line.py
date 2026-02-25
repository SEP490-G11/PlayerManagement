# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import boto3
from odoo.exceptions import ValidationError

class ZMedicalTipsLine(models.Model):
    _name = "z_obstetric.medical_tips_line"
    _description = "Medical Tips"

    service_id = fields.Many2one(
        "product.product",
        string="Medical tips name",
        domain="[('detailed_type','=', 'service')]",
        required=True,
    )
    result = fields.Char(string="Result")
    visit_id = fields.Many2one("z_appointment.appointment", ondelete="cascade")

    def create(self, vals):
        medical_tips_line = super(ZMedicalTipsLine, self).create(vals)
        
        if medical_tips_line.visit_id and not medical_tips_line.visit_id.date_assign:
            today_date = fields.Date.today()
            medical_tips_line.visit_id.write({
                'date_assign': today_date,
            })
        
        return medical_tips_line