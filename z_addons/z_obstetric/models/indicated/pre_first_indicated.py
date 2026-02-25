# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZPreFirstIndicated(models.Model):
    _name = "z_obstetric.pre_first_indicated"
    _inherit = ["z_medical_record.medical_result"]
    _description = (
        "Pregnant Pre-first ultra sound indicated"  # Siêu âm thai dưới 3 tháng
    )

    kcc = fields.Text("KCC")  # KCC
    pregnant_age_1 = fields.Text("Pregnant Age")  # Tuổi thai
    quantity_fetal = fields.Text("Quantity")  # Số lượng thai
    position_fetal = fields.Text("Position")  # Ví trí
    amniotic_sac = fields.Text("Amniotic Sac")  # KT túi ối
    heart_fetal = fields.Text("Heart")  # Tim thai
    length = fields.Text("Length")  # Chiều dài đầu mông (CR)
    biparietal = fields.Text("Biparietal")  # Lưỡng đỉnh
    gesture = fields.Text("Gesture")  # Cử động thai
    light_neck_back = fields.Text("Light of back neck")  # Khoảng sáng sau gáy
    other_image = fields.Text("Other image")  # Hình ảnh khác
    pregnant_age_2 = fields.Text("Pregnant Age")  # Tuổi thai
    expected_birth = fields.Text("Expected Birth")  # Dự kiến sinh
    is_save = fields.Boolean("Is save", default=False, tracking=True)
    
    @api.model
    def create(self, vals):
        vals["is_save"] = True
        record = super(ZPreFirstIndicated, self).create(vals)
        return record