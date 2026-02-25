# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZLensExamination(models.Model):
    _name = "z_ophthalmology.lens"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Lens examination result"

    drug_ids = fields.One2many(
        "z_medical_record.drug",
        "lens_id",
        "Prescription",
        copy=True,
    )

    biomicroscopy = fields.Text("Biomicroscopy")  # Sinh hiển vi

    # Đơn kính
    # Mắt phải
    right_eye_glasses_brand = fields.Char("Right eye glasses brand")  # Hãng kính
    right_eye_bc = fields.Char("Right eye BC")  # BC
    right_eye_p = fields.Char("Right eye P")  # P
    right_eye_dia = fields.Char("Right eye DIA")  # DIA
    right_eye_vision = fields.Char("Right eye vision")  # Thị lực
    # Mắt trái
    left_eye_glasses_brand = fields.Char("Left eye glasses brand")  # Hãng kinh
    left_eye_bc = fields.Char("Left eye BC")  # BC
    left_eye_p = fields.Char("Left eye P")  # P
    left_eye_dia = fields.Char("Left eye DIA")  # DIA
    left_eye_vision = fields.Char("Left eye vision")  # Thị lực

    # Khúc xạ chủ quan
    right_eye_subjective_refraction = fields.Char(
        "Right eye subjective refraction"
    )  # Mắt phải
    left_eye_subjective_refraction = fields.Char(
        "Left eye subjective refraction"
    )  # Mắt trái

    # Độ cong
    # Mắt phải
    right_eye_flat_k_first = fields.Char("Right eye flat k first")
    right_eye_flat_k_second = fields.Char("Right eye flat k second")
    right_eye_flat_k_third = fields.Char("Right eye flat k third")
    right_eye_steep_k_first = fields.Char("Right eye steep k first")
    right_eye_steep_k_second = fields.Char("Right eye steep k second")
    right_eye_steep_k_third = fields.Char("Right eye steep k third")
    # Mắt trái
    left_eye_flat_k_first = fields.Char("Left eye flat k first")
    left_eye_flat_k_second = fields.Char("Left eye flat k second")
    left_eye_flat_k_third = fields.Char("Left eye flat k third")
    left_eye_steep_k_first = fields.Char("Left eye steep k first")
    left_eye_steep_k_second = fields.Char("Left eye steep k second")
    left_eye_steep_k_third = fields.Char("Left eye steep k third")

    # Đường kính giác mạc
    right_eye_corneal_diameter = fields.Char("Right eye corneal diameter")  # Mắt phải
    left_eye_corneal_diameter = fields.Char("Left eye corneal diameter")  # Mắt trái

    # Đường kính mống mắt
    right_eye_iris_diameter = fields.Char("Right eye iris diameter")  # Mắt phải
    left_eye_iris_diameter = fields.Char("Left eye iris diameter")  # Mắt trái

    # Kích thước đồng tử
    right_eye_pupil_size = fields.Char("Right eye pupil size")  # Mắt phải
    left_eye_pupil_size = fields.Char("Left eye pupil size")  # Mắt trái

    # Độ sâu tiền phòng
    right_eye_anterior_chamber_depth = fields.Char(
        "Right eye anterior chamber depth"
    )  # Mắt phải
    left_eye_anterior_chamber_depth = fields.Char(
        "Left eye anterior chamber depth"
    )  # Mắt trái

    # Chiều dài trục nhãn cầu
    right_eye_eyeball_axis_length = fields.Char(
        "Right eye eyeball axis length"
    )  # Mắt phải
    left_eye_eyeball_axis_length = fields.Char(
        "Left eye eyeball axis length"
    )  # Mắt trái

    trial_lenses = fields.Json("Trial lenses", default=[])

    eye_eyeball_axis_length = fields.Html(
        string="Eye eyeball axis length",
        compute="_compute_eye_eyeball_axis_length",
        store=False,
    )
    # Ghi chú phiếu khám
    note_medical_exam = fields.Text(string="Note medical exam")

    @api.depends("right_eye_eyeball_axis_length", "left_eye_eyeball_axis_length")
    def _compute_eye_eyeball_axis_length(self):
        for record in self:
            record.eye_eyeball_axis_length = (
                _("Left eye:")
                + " "
                + str(record.right_eye_eyeball_axis_length or "")
                + " <br> "
                + _("Right eye:")
                + " "
                + str(record.right_eye_eyeball_axis_length or "")
            )

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
            "z_ophthalmology.action_report_lens"
        )
        return action
