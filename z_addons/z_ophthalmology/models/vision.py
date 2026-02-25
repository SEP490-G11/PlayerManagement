# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ZVisionExamination(models.Model):
    _name = "z_ophthalmology.vision"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Low vision examination result"

    drug_ids = fields.One2many(
        "z_medical_record.drug", "vision_id", "Prescription", copy=True
    )

    # Khám lâm sàng
    # Mắt phải
    right_eye_close_without_glasses = fields.Char(
        "Right eye close without glasses"
    )  # Gần không kính
    right_eye_far_without_glasses = fields.Char(
        "Right eye far without glasses"
    )  # Xa không kính
    right_eye_close_old_glasses = fields.Char(
        "Right eye close old glasses"
    )  # Gần kính cũ
    right_eye_far_old_glasses = fields.Char("Right eye far old glasses")  # Xa kính cũ
    right_eye_sbdt = fields.Char("Right eye SBDT")  # SBĐT
    right_eye_subjective_refraction = fields.Char(
        "Right eye subjective refraction"
    )  # Khúc xạ chủ quan
    right_eye_contrast = fields.Char("Right eye contrast")  # Thị lực tương phản
    right_eye_with_glare = fields.Char(
        "Right eye with glare"
    )  # Thị lực với ánh sáng chói

    # Mắt trái
    left_eye_close_without_glasses = fields.Char(
        "Left eye close without glasses"
    )  # Gần không kính
    left_eye_far_without_glasses = fields.Char(
        "Left eye far without glasses"
    )  # Xa không kính
    left_eye_close_old_glasses = fields.Char(
        "Left eye close old glasses"
    )  # Gần kính cũ
    left_eye_far_old_glasses = fields.Char("Left eye far old glasses")  # Xa kính cũ
    left_eye_sbdt = fields.Char("Left eye SBDT")  # SBĐT
    left_eye_subjective_refraction = fields.Char(
        "Left eye subjective refraction"
    )  # Khúc xạ chủ quan
    left_eye_contrast = fields.Char("Left eye contrast")  # Thị lực tương phản
    left_eye_with_glare = fields.Char(
        "Left eye with glare"
    )  # Thị lực với ánh sáng chói

    # Hai mắt
    eyes_close_without_glasses = fields.Char(
        "Eyes close without glasses"
    )  # Gần không kính
    eyes_far_without_glasses = fields.Char("Eyes far without glasses")  # Xa không kính
    eyes_close_old_glasses = fields.Char("Eyes close old glasses")  # Gần kính cũ
    eyes_far_old_glasses = fields.Char("Eyes far old glasses")  # Xa kính cũ
    eyes_sbdt = fields.Char("Eyes SBDT")  # SBĐT
    eyes_subjective_refraction = fields.Char(
        "Eyes subjective refraction"
    )  # Khúc xạ chủ quan
    right_left_eye_add = fields.Char("Right left eyes ADD")  # ADD
    eyes_add = fields.Char("Eyes ADD")  # ADD
    eyes_contrast = fields.Char("Eyes contrast")  # Thị lực tương phản
    eyes_with_glare = fields.Char("Eyes with glare")  # Thị lực với ánh sáng chói

    # Sắc giác
    color_sense_mp = fields.Char("Color sense MP")  # MP
    color_sense_mt = fields.Char("Color sense MT")  # MT
    color_sense_test = fields.Char("Color sense test")  # Test
    # NPC
    npc_mp = fields.Char("NPC MP")  # MP
    npc_mt = fields.Char("NPC MT")  # MT
    npc_test = fields.Char("NPC test")  # Test
    eoms = fields.Char("EOMs")  # EOMs
    # KCDT
    kcdt_close = fields.Char("KCDT close")  # Gần
    kcdt_far = fields.Char("KCDT far")  # Xa
    pupil = fields.Char("Pupil")
    light_perrl = fields.Char("Light perrl")  # Perrl sáng
    dark_perrl = fields.Char("Dark perrl")  # Perrl tối
    # Cover test
    cover_test_dsc = fields.Char("Cover test DSC")
    cover_test_dcc = fields.Char("Cover test DCC")
    cover_test_nsc = fields.Char("Cover test NSC")
    cover_test_ncc = fields.Char("Cover test NCC")
    # Thị trường
    mp_exam = fields.Char("MP exam")
    mt_exam = fields.Char("MT exam")
    fas = fields.Char("FAS")
    ffs = fields.Char("FFS")
    fvs = fields.Char("FVS")

    # Đánh giá khiếm thị
    # Trợ cụ đang sử dụng
    tool_in_use_name = fields.Char("Tool in use name")  # Tên
    tool_in_use_wattage = fields.Char("Tool in use wattage")  # Công suất
    tool_in_use_right_eye = fields.Char("Tool in use right eye")  # Mắt phải
    tool_in_use_left_eye = fields.Char("Tool in use left eye")  # Mắt trái
    tool_in_use_status = fields.Char("Tool in use status")  # Tình trạng
    # Trợ cụ nhìn gần
    close_up_tool_name = fields.Char("Close up tool name")  # Tên
    close_up_tool_wattage = fields.Char("Close up tool wattage")  # Công suất
    close_up_tool_right_eye = fields.Char("Close up tool right eye")  # Mắt phải
    close_up_tool_left_eye = fields.Char("Close up tool left eye")  # Mắt trái
    close_up_tool_status = fields.Char("Close up tool status")  # Tình trạng
    # Trợ cụ nhìn xa
    foresight_tool_name = fields.Char("Foresight tool name")  # Tên
    foresight_tool_wattage = fields.Char("Foresight tool wattage")  # Công suất
    foresight_tool_right_eye = fields.Char("Foresight tool right eye")  # Mắt phải
    foresight_tool_left_eye = fields.Char("Foresight tool left eye")  # Mắt trái
    foresight_tool_status = fields.Char("Foresight tool status")  # Tình trạng
    # Trợ cụ phi quang học
    non_optical_tool_name = fields.Char("Non optical tool name")  # Tên
    non_optical_tool_wattage = fields.Char("Non optical tool wattage")  # Công suất
    non_optical_tool_right_eye = fields.Char("Non optical tool right eye")  # Mắt phải
    non_optical_tool_left_eye = fields.Char("Non optical tool left eye")  # Mắt trái
    non_optical_tool_status = fields.Char("Non optical tool status")  # Tình trạng

    # Đơn kính
    right_eye_glasses_prescription = fields.Char(
        "Right eye glasses prescription"
    )  # Mắt phải
    left_eye_glasses_prescription = fields.Char(
        "Left eye glasses prescription"
    )  # Mắt trái

    # Ghi chú phiếu khám
    note_medical_exam = fields.Text(string="Note medical exam")

    @api.onchange("drug_ids")
    def _onchange_line_ids(self):
        products = self.drug_ids.mapped("product_id")
        for product in products:
            product_lines = self.drug_ids.filtered(lambda l: l.product_id == product)
            if len(product_lines) > 1:
                product_lines[0].quantity = sum(product_lines.mapped("quantity"))
                self.drug_ids = [(2, product_lines[1:].id, 0)]

    def action_print(self):
        action = self.env["ir.actions.report"]._for_xml_id(
            "z_ophthalmology.action_report_vision"
        )
        return action
