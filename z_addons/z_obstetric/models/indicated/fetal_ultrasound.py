# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZFetalUltrasound(models.Model):
    _name = "z_obstetric.fetal_ultrasound"
    _inherit = ["z_medical_record.medical_result"]
    _description = (
        "4D Fetal Ultrasound"  # Siêu âm thai 4D
    )

    quantity_fetal = fields.Text("Quantity")  # Số lượng thai
    edge_of_skull = fields.Text("Edge of the skull")  # Bờ hộp sọ
    head_circumference = fields.Text("Head circumference")  # Chu vi đầu
    nasal_spine = fields.Text("Nasal spine")  # Xương sống mũi
    anterior_abdominal_wall = fields.Text("Anterior abdomnial wall")  # Thành bụng trước
    stomach_image = fields.Text("Stomach image")  # Hình ảnh dạ dày
    spine = fields.Text("Spine")  # Cột sống
    femur_length = fields.Text("Femur length")  # Chiều dài xương đùi 
    limb_posture= fields.Text("Limb posture")  # Tư thế các chi
    amniotic_status = fields.Text("Amniotic status")  # Tình trạng ối
    head_butt_length = fields.Text("Head butt length")  # Chiều dài đầu mông
    fetal_weight = fields.Text("Fetal weight")  # Trọng lượng thai
    fetal_movement = fields.Text("Fetal movement")  # Cử động thai nhi
    diagonal_diameter = fields.Text("Diagonal diameter")  # Đường kính lưỡng đinh
    midline_structure = fields.Text("Midline structure")  # Cấu trúc đường giữa
    fetal_heart_rate = fields.Text("Fetal heart rate")  # Nhịp tim thai (lần/phút)
    abdominal_circumference = fields.Text("Abdominal circumference")  # Chu vi bụng
    bladder = fields.Text("Bladder")  # Bàng quang
    limbs = fields.Text("Limbs")  # Các chi (3 đoạn)
    foot_length = fields.Text("Foot length")  # Chiều dài bàn chân
    placenta_position = fields.Text("Placenta position")  # Vị trí rau bám
    umbilical_cord = fields.Text("Umbilical cord")  # Dây rốn (3 mạch máu)
    light_neck_back = fields.Text("Light of back neck")  # Khoảng sáng sau gáy
    expected_birth = fields.Text("Expected birth")  # Dự kiến sinh
    other_image = fields.Text("Other image")  # Hình ảnh khác
    diagnose = fields.Text("Diagnose")  # Chẩn đoán
    note = fields.Text("Note")  # Lưu ý
    is_save = fields.Boolean("Is save", default=False, tracking=True)
    
    @api.model
    def create(self, vals):
        vals["is_save"] = True
        record = super(ZFetalUltrasound , self).create(vals)
        return record