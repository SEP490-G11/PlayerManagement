# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZPostFirstIndicated(models.Model):
    _name = "z_obstetric.post_first_indicated"
    _inherit = ["z_medical_record.medical_result"]
    _description = (
        "Pregnant Post-first ultra sound indicated"  # Siêu âm thai trên 3 tháng
    )

    quantity_fetal = fields.Text("Quantity")  # Số lượng thai
    position_fetal = fields.Text("Position")  # Ngôi
    heart_fetal = fields.Text("Heart")  # Tim thai
    biparietal = fields.Text("Biparietal")  # Đường kính lưỡng đỉnh(BPD)
    femur_length = fields.Text("Femur length")  # Chiều dài xương đùi(FL)
    abdominal_circumference = fields.Text("Abdominal circumference")  # Chu vi bụng(AC)
    weight = fields.Text("Weight")  # Cân nặng
    pregnant_age = fields.Text("Pregnant Age")  # Tuổi thai
    expected_birth = fields.Text("Expected Birth")  # Dự kiến sinh
    amniotic_sac = fields.Text("Amniotic Sac")  # Ối
    placenta = fields.Text("Placenta")  # Nhau
    placenta_position = fields.Text("Placenta Position")  # Vị trí nhau thai
    maturity_level = fields.Selection(
        [
            ("1", "Calcium level 0"),
            ("2", "Calcium level 1"),
            ("3", "Calcium level 1-2"),
            ("4", "Calcium level 2"),
        ],
        string="Maturity Level",
    ) # Độ trưởng thành
    other_image = fields.Text("Other image")  # Hình ảnh khác
    is_save = fields.Boolean("Is save", default=False, tracking=True)
    
    @api.model
    def create(self, vals):
        vals["is_save"] = True
        record = super(ZPostFirstIndicated, self).create(vals)
        return record
