# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZUltraSound(models.Model):
    _name = "z_obstetric.ultra_sound"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Ultra sound examination result"

    # Diagnose
    menstrual = fields.Text("Menstrual")  # Kinh nguyệt
    menstrual_cycle = fields.Text("Cycle")  # Chu kì
    menstrual_day = fields.Text("Menstrual Day")  # Ngày kinh

    # Uterus
    position = fields.Text("Position")  # Tư thế
    size = fields.Text("Size(mm)")  # Kích thước (mm)
    other_image = fields.Text("Other image")  # Hình ảnh khác

    # Monitoring ovulation
    date = fields.Date("Date")  # Ngày
    ovulation_date = fields.Text("Ovulation Date")  # Ngày chu kì
    mucosa = fields.Text("Mucosa")  # Niêm mạc
    left_ovary = fields.Text("Left ovary")  # Buồng trứng trái
    right_ovary = fields.Text("Right ovary")  # Buồng trứng phải
    mocous_douglas = fields.Text("Mocous Douglas")  # Dịch cùng đồ
