# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ZBinocularVisionExamination(models.Model):
    _name = "z_ophthalmology.binocular_vision"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Binocular vision examination result"

    drug_ids = fields.One2many(
        "z_medical_record.drug", "binocular_vision_id", "Prescription", copy=True
    )

    # Hệ phân tụ
    cover_test = fields.Char("Cover test")  # Cover test
    strabismus = fields.Char("Strabismus")  # Độ lác xa
    near_strabismus = fields.Char("Near strabismus")  # Độ lác gần
    npc = fields.Char("NPC")  # NPC
    pfv = fields.Char("PFV")  # PFV
    nfv = fields.Char("NFV")  # NFV

    # Hệ điều tiết
    # Mắt phải
    right_eye_aa = fields.Char("Right eye AA")  # AA
    right_eye_mem = fields.Char("Right eye MEM")  # MEM
    right_eye_maf = fields.Char("Right eye MAF")  # MAF
    # Mắt trái
    left_eye_aa = fields.Char("Left eye AA")  # AA
    left_eye_mem = fields.Char("Left eye MEM")  # MEM
    left_eye_maf = fields.Char("Left eye MAF")  # MAF
    # Hai mắt
    eyes_aa = fields.Char("Eye AA")  # AA
    eyes_nra_pra = fields.Char("Eye NRA/PRA")  # NRA/PRA
    eyes_baf = fields.Char("Eye BAF")  # BAF

    other_test = fields.Char("Other test")  # Các test khác
    tracking_element = fields.Text("Tracking element")  # Yếu tố theo dõi
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
            "z_ophthalmology.action_report_binocular_vision"
        )
        return action
