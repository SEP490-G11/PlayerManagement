# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZGynecologicalUltrasound(models.Model):
    _name = "z_obstetric.gyn_ult"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Gynecological ultrasound"  # Siêu âm phụ khoa

    position = fields.Text("Position")  # Tư thế
    size = fields.Text("Size")  # Kích thước
    structure = fields.Text("Structure")  # Cấu trúc
    endometrium = fields.Text("Endometrium")  # Niêm mạc tử cung
    other_image_uterus = fields.Text("Other image")  # Hình ảnh khác
    right_ovary = fields.Text("Right ovary")  # Buồng trứng phải
    left_ovary = fields.Text("Left ovary")  # Buồng trứng trái
    douglas = fields.Text("Douglas")  # Douglas
    other_image = fields.Text("Other image")  # Hình ảnh khác
    is_save = fields.Boolean("Is save", default=False, tracking=True)

    @api.model
    def create(self, vals):
        vals["is_save"] = True
        record = super(ZGynecologicalUltrasound, self).create(vals)
        return record
