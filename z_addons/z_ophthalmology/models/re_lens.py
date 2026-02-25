# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ZReLens(models.Model):
    _name = "z_ophthalmology.re_lens"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Lens reexamination result"

    drug_ids = fields.One2many(
        "z_medical_record.drug", "re_lens_id", "Prescription", copy=True
    )

    # Mắt phải
    right_eye_ktx = fields.Char("Right eye KTX")  # KTX
    right_eye_orx = fields.Char("Right eye ORx")  # ORx
    right_eye_shv = fields.Char("Right eye SHV")  # SHV
    right_eye_eyeball_axis_length = fields.Char(
        "Right eye eyeball axis length"
    )  # Chiều dài trục nhãn cầu
    # Mắt trái
    left_eye_ktx = fields.Char("Left eye KTX")  # KTX
    left_eye_orx = fields.Char("Left eye ORx")  # ORx
    left_eye_shv = fields.Char("Left eye SHV")  # SHV
    left_eye_eyeball_axis_length = fields.Char(
        "Left eye eyeball axis length"
    )  # Chiều dài trục nhãn cầu

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
            "z_ophthalmology.action_report_re_lens"
        )
        return action
