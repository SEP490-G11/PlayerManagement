# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZMedicalTest(models.Model):
    _name = "z_obstetric.medical_test"
    _inherit = ["z_medical_record.medical_result","mail.thread", "mail.activity.mixin"]
    _description = "Medical test"
    
    medical_test_line_ids = fields.One2many(
        "z_obstetric.medical_test_line", "medical_test_id", string="Services in test", copy=True
    )
    
    
  