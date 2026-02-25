# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.z_ophthalmology.controllers.research_utils import ZResearchUtils


class ZComprehensive(models.Model):
    _name = "z_ophthalmology.comprehensive"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Comprehensive examination result"

    drug_ids = fields.One2many(
        "z_medical_record.drug", "comprehensive_id", "Prescription", copy=True
    )
    # Sinh trắc học
    # Mắt phải
    right_eye_eyeball_axis_length = fields.Float(
        string="Right eye eyeball axis length", store=True, default=False
    )  # Chiều dài trục nhãn cầu
    right_eye_gm_thickness = fields.Float("Right eye gm thickness")  # Chiều dày GM
    right_eye_pupil_size = fields.Float("Right eye pupil size")  # Kích thước đồng tử
    right_eye_acd = fields.Float("Right eye ACD")  # ACD
    right_eye_steep_or_flat_k_first = fields.Float(
        string="Right eye steep k or flat k (D)", store=True
    )  # Steep k or flat k (D)
    right_eye_steep_or_flat_k_second = fields.Float(
        string="Right eye steep k or flat k (D)",
        store=True,
    )  # Steep k or flat k (D)
    right_eye_steep_or_flat_k_mm_first = fields.Float(
        string="Right eye steep k or flat k (mm)",
        store=True,
        compute="_compute_by_axis_and_first_flat_right_eye",
    )  # Steep k or flat k (mm)
    right_eye_steep_or_flat_k_mm_second = fields.Float(
        string="Right eye steep k or flat k (mm)",
        store=True,
        compute="_compute_by_axis_and_second_flat_right_eye",
    )  # Steep k or flat k (mm)
    right_eye_steep_or_flat_k_mm_third = fields.Float(
        string="Right eye steep k or flat k (mm)",
        store=True,
        compute="_compute_right_eye_steep_or_flat_k_mm_third",
    )  # Steep k or flat k (mm)
    right_ocular_axial_length_GM_radius_of_curvature_first = fields.Float(
        string="Left ocular axial length/GM radius of curvature",
        store=True,
        compute="_compute_by_axis_and_first_flat_right_eye",
    )  # Chiều dài trục nhãn cầu/Bán kính cong GM (AL/CR)
    right_ocular_axial_length_GM_radius_of_curvature_second = fields.Float(
        string="Left ocular axial length/GM radius of curvature",
        store=True,
        compute="_compute_by_axis_and_second_flat_right_eye",
    )  # Chiều dài trục nhãn cầu/Bán kính cong GM (AL/CR)
    right_ocular_axial_length_GM_radius_of_curvature_third = fields.Float(
        string="Left ocular axial length/GM radius of curvature",
        store=True,
        compute="_compute_right_ocular_axial_length_GM_radius_of_curvature_third",
    )  # Chiều dài trục nhãn cầu/Bán kính cong GM (AL/CR)

    right_intraocular_pressure = fields.Char("Right intraocular pressure")
    left_intraocular_pressure = fields.Char("Left intraocular pressure")
    # Mắt trái
    left_eye_eyeball_axis_length = fields.Float(
        string="Left eye eyeball axis length",
        store=True,
    )  # Chiều dài trục nhãn cầu
    left_eye_gm_thickness = fields.Float("Left eye gm thickness")  # Chiều dày GM
    left_eye_pupil_size = fields.Float("Left eye pupil size")  # Kích thước đồng tử
    left_eye_acd = fields.Float("Left eye ACD")  # ACD
    left_eye_steep_or_flat_k_first = fields.Float(
        string="Left eye steep k or flat k (D)",
        store=True,
    )
    left_eye_steep_or_flat_k_second = fields.Float(
        string="Left eye steep k or flat k (D)",
        store=True,
    )
    # Steep k or flat k (D)
    left_eye_steep_or_flat_k_mm_first = fields.Float(
        string="Left eye steep k or flat k (mm)",
        store=True,
        compute="_compute_by_axis_and_first_flat_left_eye",
    )  # Steep k or flat k (mm)
    left_eye_steep_or_flat_k_mm_second = fields.Float(
        string="Left eye steep k or flat k (mm)",
        store=True,
        compute="_compute_by_axis_and_second_flat_left_eye",
    )  # Steep k or flat k (mm)
    left_eye_steep_or_flat_k_mm_third = fields.Float(
        string="Left eye steep k or flat k (mm)",
        store=True,
        compute="_compute_left_eye_steep_or_flat_k_mm_third",
    )  # Steep k or flat k (mm)

    left_ocular_axial_length_GM_radius_of_curvature_first = fields.Float(
        string="Left ocular axial length/GM radius of curvature",
        store=True,
        compute="_compute_by_axis_and_first_flat_left_eye",
    )  # Chiều dài trục nhãn cầu/Bán kính cong GM (AL/CR)
    left_ocular_axial_length_GM_radius_of_curvature_second = fields.Float(
        string="Left ocular axial length/GM radius of curvature",
        store=True,
        compute="_compute_by_axis_and_second_flat_left_eye",
    )  # Chiều dài trục nhãn cầu/Bán kính cong GM (AL/CR)
    left_ocular_axial_length_GM_radius_of_curvature_third = fields.Float(
        string="Left ocular axial length/GM radius of curvature",
        store=True,
        compute="_compute_left_ocular_axial_length_GM_radius_of_curvature_third",
    )  # Chiều dài trục nhãn cầu/Bán kính cong GM (AL/CR)
    # Thị lực mắt phải
    right_eye_without_glasses = fields.Char("Right eye without glasses")  # Không kính
    right_eye_old_glasses = fields.Char("Right eye old glasses")  # mắt phải kính cũ
    right_eye_old_glasses_unit = fields.Char(
        "Right eye old glasses unit"
    )  # Đơn vị kính cũ

    # Thị lực mắt trái
    left_eye_without_glasses = fields.Char("Left eye without glasses")  # Không kính
    left_eye_old_glasses = fields.Char("Left eye old glasses")  # Kính cũ
    left_eye_old_glasses_unit = fields.Char(
        "Left eye old glasses unit"
    )  # Đơn vị kính cũ

    # Thị lực hai mắt
    eyes_without_glasses = fields.Char("Eyes without glasses")  # Không kính
    eyes_old_glasses = fields.Char("Eyes old glasses")  # Kính cũ
    eyes_old_glasses_unit = fields.Char("Eyes old glasses unit")  # Đơn vị kính cũ

    measurement_type = fields.Selection(
        [("SC", "SC"), ("CC", "CC")], default="SC"
    )  # thị lực gần
    oculus_dexter = fields.Char("Oculus dexter")  # thị lực gần mắt phải
    oculus_sinister = fields.Char("Oculus sinister")  # thị lực gần mắt trái

    # Hệ phân tụ và vận nhãn
    ct = fields.Char("CT")
    npc = fields.Char("NPC")
    eom = fields.Char("EOM")

    # Tật khúc xạ - trước liệt
    add = fields.Char("ADD")  # ADD
    # Mắt phải
    right_eye_objective_anterior_refraction_first = fields.Char(
        string="Right eye objective anterior refraction first",
        store=True,
    )  # Khúc xạ khách quan 1
    right_eye_objective_anterior_refraction_second = fields.Char(
        "Right eye objective anterior refraction second"
    )  # Khúc xạ khách quan 2
    right_eye_objective_anterior_refraction_third = fields.Char(
        "Right eye objective anterior refraction third"
    )  # Khúc xạ khách quan 3
    right_eye_objective_anterior_refraction_unit = fields.Char(
        "Right eye objective anterior refraction unit"
    )  # Đơn vị khúc xạ khách quan
    right_eye_subjective_anterior_refraction = fields.Char(
        "Right eye subjective anterior refraction"
    )  # Khúc xạ chủ quan
    right_eye_subjective_anterior_refraction_unit = fields.Char(
        "Right eye subjective anterior refraction unit"
    )  # Đơn vị khúc xạ chủ quan
    # Mắt trái
    left_eye_objective_anterior_refraction_first = fields.Char(
        string="Left eye objective anterior refraction first",
        store=True,
    )  # Khúc xạ khách quan 1
    left_eye_objective_anterior_refraction_second = fields.Char(
        "Left eye objective anterior refraction second"
    )  # Khúc xạ khách quan 2
    left_eye_objective_anterior_refraction_third = fields.Char(
        "Left eye objective anterior refraction third"
    )  # Khúc xạ khách quan 2
    left_eye_objective_anterior_refraction_unit = fields.Char(
        "Left eye objective anterior refraction unit"
    )  # Đơn vị khúc xạ khách quan
    left_eye_subjective_anterior_refraction = fields.Char(
        "Left eye subjective anterior refraction"
    )  # Khúc xạ chủ quan
    left_eye_subjective_anterior_refraction_unit = fields.Char(
        "Left eye subjective anterior refraction unit"
    )  # Đơn vị chủ xạ khách quan

    # Tật khúc xạ - sau liệt
    cyclogyl = fields.Boolean(string="Cyclogyl 1%", default=False)
    atropin = fields.Boolean(string="Atropin 0.5%", default=False)

    @api.onchange("cyclogyl")
    def _onchange_cyclogyl(self):
        if self.cyclogyl:
            self.atropin = False

    @api.onchange("atropin")
    def _onchange_atropin(self):
        if self.atropin:
            self.cyclogyl = False

    # Mắt phải
    right_eye_objective_paralytic_refraction_first = fields.Char(
        string="Right eye objective paralytic refraction first",
        store=True,
    )  # Khúc xạ khách quan 1
    right_eye_objective_paralytic_refraction_second = fields.Char(
        "Right eye objective paralytic refraction second"
    )  # Khúc xạ khách quan 2
    right_eye_objective_paralytic_refraction_third = fields.Char(
        "Right eye objective paralytic refraction third"
    )  # Khúc xạ khách quan 2
    right_eye_objective_paralytic_refraction_unit = fields.Char(
        "Right eye objective paralytic refraction unit"
    )  # Đơn vị khúc xạ khách quan
    right_eye_subjective_paralytic_refraction = fields.Char(
        "Right eye subjective paralytic refraction"
    )  # Khúc xạ chủ quan
    right_eye_subjective_paralytic_refraction_unit = fields.Char(
        "Right eye subjective paralytic refraction unit"
    )  # Đơn vị khúc xạ chủ quan
    # Mắt trái
    left_eye_objective_paralytic_refraction_first = fields.Char(
        string="Left eye objective paralytic refraction first",
        store=True,
    )  # Khúc xạ khách quan 1
    left_eye_objective_paralytic_refraction_second = fields.Char(
        "Left eye objective paralytic refraction second"
    )  # Khúc xạ khách quan 2
    left_eye_objective_paralytic_refraction_third = fields.Char(
        "Left eye objective paralytic refraction third"
    )  # Khúc xạ khách quan 2
    left_eye_objective_paralytic_refraction_unit = fields.Char(
        "Left eye objective paralytic refraction unit"
    )  # Đơn vị khúc xạ khách quan
    left_eye_subjective_paralytic_refraction = fields.Char(
        "Left eye subjective paralytic refraction"
    )  # Khúc xạ chủ quan
    left_eye_subjective_paralytic_refraction_unit = fields.Char(
        "Left eye subjective paralytic refraction unit"
    )  # Đơn vị chủ xạ khách quan

    eye_health = fields.Text("Eye health")  # Sức khoẻ mắt
    diagnose = fields.Text("Diagnose", tracking=True)  # Chẩn đoán

    # Đơn kính
    right_eye_glasses_prescription = fields.Char(
        "Right eye glasses prescription"
    )  # Mắt phải
    left_eye_glasses_prescription = fields.Char(
        "Left eye glasses prescription"
    )  # Mắt trái
    add_glasses_prescription = fields.Char("Add glasses prescription")  # ADD
    tracking_element = fields.Text("Tracking element")  # Yếu tố theo dõi
    family_history_of_myopia = fields.Selection(
        [("1", _("No Body")), ("2", _("Parents")), ("3", _("Both"))],
        string="Family history of myopia",
        tracking=True,
        store=True,
    )

    # Tiền cận thị
    eyeball_axis_length_in_right_eye_with_potential_myopia = fields.Char(
        string="Eyeball axis length in right eye with potential myopia",
        store=True,
        readonly=True,
    )  # Mắt phải
    eyeball_axis_length_in_left_eye_with_potential_myopia = fields.Char(
        string="Eyeball axis length in left eye with potential myopia",
        store=True,
        readonly=True,
    )  # Mắt trái
    right_eyeball_axis_length_point = fields.Float(
        string="Right eyeball axis length point",
        store=True,
        compute="_compute_by_axis_and_first_flat_right_eye",
    )  # Điểm mắt phải
    left_eyeball_axis_length_point = fields.Char(
        string="Left eyeball axis length point",
        store=True,
        compute="_compute_by_axis_and_first_flat_left_eye",
    )  # Điểm mắt trái
    right_eye_classification = fields.Char(
        string="Right eye classification",
        compute="_compute_right_eye_classification",
        default="",
        store=True,
        readonly=True,
    )  # Phân loại mắt phải
    left_eye_classification = fields.Char(
        string="Left eye classification",
        compute="_compute_left_eye_classification",
        default="",
        store=True,
        readonly=True,
    )  # Phân loại mắt trái
    family_history_of_myopia_value = fields.Char(
        string="Family history of myopia value",
        store=True,
        compute="_compute_history_of_myopia_point",
    )  # Tiền sử gia đình cận thị
    family_history_of_myopia_point = fields.Float(
        string="Family history of myopia point",
        store=True,
        compute="_compute_history_of_myopia_point",
    )  # Tiền sử gia đình cận thị
    pre_myopia_refractive_error_right_eye_value = fields.Char(
        string="Pre myopia refractive error right eye value",
        store=True,
        compute="_compute_pre_myopia_refractive_error_right_eye_value",
    )  # Tật khúc xạ giá trị mắt phải
    pre_myopia_refractive_error_left_eye_value = fields.Char(
        string="Pre myopia refractive error left eye value",
        store=True,
        compute="_compute_pre_myopia_refractive_error_left_eye_value",
    )  # Tật khúc xạ giá trị mắt trái
    pre_myopia_refractive_error_right_eye_point = fields.Char(
        string="Pre myopia refractive error right eye point",
        store=True,
        compute="_compute_pre_myopia_refractive_error_right_eye_point",
    )  # Điểm tật khúc xạ mắt phải
    pre_myopia_refractive_error_left_eye_point = fields.Char(
        string="Pre myopia refractive error left eye point",
        store=True,
        compute="_compute_pre_myopia_refractive_error_left_eye_point",
    )  # Điểm tật khúc xạ mắt trái
    customer_age = fields.Integer(string="Customer age", related="customer_id.age")
    is_valid_for_research = fields.Boolean(
        string="Is valid for research", compute="_compute_is_valid_for_research"
    )
    # Ghi chú phiếu khám
    note_medical_exam = fields.Text(string="Note medical exam")
    right_amsler_test = fields.Char("Right amsler test", size=150)
    left_amsler_test = fields.Char("Left amsler test", size=150)

    @api.model
    def default_get(self, fields_list):
        defaults = super(ZComprehensive, self).default_get(fields_list)
        context = self.env.context
        if "default_visit_id" in context:
            defaults["visit_id"] = context.get("default_visit_id")
        if "default_customer_id" in context:
            defaults["customer_id"] = context.get("default_customer_id")
        if "default_optometrist_id" in context:
            defaults["optometrist_id"] = context.get("default_optometrist_id")
        if "default_examiner_id" in context:
            defaults["examiner_id"] = context.get("default_examiner_id")
        if "default_examination_date" in context:
            defaults["examination_date"] = context.get("default_examination_date")
        if "default_code" in context:
            defaults["code"] = context.get("default_code")
        if "default_examination_type" in context:
            defaults["examination_type"] = context.get("default_examination_type")

        return defaults

    @api.depends("customer_age")
    def _compute_is_valid_for_research(self):
        for rec in self:
            rec.is_valid_for_research = 6 <= rec.customer_age <= 9

    @api.onchange("drug_ids")
    def _onchange_line_ids(self):
        products = self.drug_ids.mapped("product_id")
        for product in products:
            product_lines = self.drug_ids.filtered(lambda l: l.product_id == product)
            if len(product_lines) > 1:
                product_lines[0].quantity = sum(product_lines.mapped("quantity"))
                self.drug_ids = [(2, product_lines[1:].id, 0)]

    @api.depends("right_eye_eyeball_axis_length", "right_eye_steep_or_flat_k_first")
    def _compute_by_axis_and_first_flat_right_eye(self):
        for rec in self:
            test = ZResearchUtils.calculate_ocular_axial_length_gm_radius_of_curvature(
                rec.right_eye_eyeball_axis_length,
                rec.right_eye_steep_or_flat_k_first,
                rec.customer_age,
            )
            rec.right_eye_steep_or_flat_k_mm_first = test[0]
            rec.right_ocular_axial_length_GM_radius_of_curvature_first = test[1]
            rec.right_eyeball_axis_length_point = test[2]

    @api.depends("right_eye_eyeball_axis_length", "right_eye_steep_or_flat_k_second")
    def _compute_by_axis_and_second_flat_right_eye(self):
        for rec in self:
            test = ZResearchUtils.calculate_ocular_axial_length_gm_radius_of_curvature(
                rec.right_eye_eyeball_axis_length,
                rec.right_eye_steep_or_flat_k_second,
                rec.customer_age,
            )
            rec.right_eye_steep_or_flat_k_mm_second = test[0]
            rec.right_ocular_axial_length_GM_radius_of_curvature_second = test[1]

    @api.depends(
        "right_ocular_axial_length_GM_radius_of_curvature_second",
        "right_ocular_axial_length_GM_radius_of_curvature_first",
    )
    def _compute_right_ocular_axial_length_GM_radius_of_curvature_third(self):
        for rec in self:
            if rec.right_eye_steep_or_flat_k_mm_third == 0:
                rec.right_ocular_axial_length_GM_radius_of_curvature_third = 0
            else:
                rec.right_ocular_axial_length_GM_radius_of_curvature_third = round(
                    rec.right_eye_eyeball_axis_length
                    / rec.right_eye_steep_or_flat_k_mm_third,
                    3,
                )

    @api.depends(
        "right_eye_steep_or_flat_k_mm_second", "right_eye_steep_or_flat_k_mm_first"
    )
    def _compute_right_eye_steep_or_flat_k_mm_third(self):
        for rec in self:
            rec.right_eye_steep_or_flat_k_mm_third = ZResearchUtils.sum_if_num(
                rec.right_eye_steep_or_flat_k_mm_second,
                rec.right_eye_steep_or_flat_k_mm_first,
            )

    @api.depends("left_eye_eyeball_axis_length", "left_eye_steep_or_flat_k_first")
    def _compute_by_axis_and_first_flat_left_eye(self):
        for rec in self:
            test = ZResearchUtils.calculate_ocular_axial_length_gm_radius_of_curvature(
                rec.left_eye_eyeball_axis_length,
                rec.left_eye_steep_or_flat_k_first,
                rec.customer_age,
            )
            rec.left_eye_steep_or_flat_k_mm_first = test[0]
            rec.left_ocular_axial_length_GM_radius_of_curvature_first = test[1]
            rec.left_eyeball_axis_length_point = test[2]

    @api.depends("left_eye_eyeball_axis_length", "left_eye_steep_or_flat_k_second")
    def _compute_by_axis_and_second_flat_left_eye(self):
        for rec in self:
            test = ZResearchUtils.calculate_ocular_axial_length_gm_radius_of_curvature(
                rec.left_eye_eyeball_axis_length,
                rec.left_eye_steep_or_flat_k_second,
                rec.customer_age,
            )
            rec.left_eye_steep_or_flat_k_mm_second = test[0]
            rec.left_ocular_axial_length_GM_radius_of_curvature_second = test[1]

    @api.depends(
        "left_ocular_axial_length_GM_radius_of_curvature_second",
        "left_ocular_axial_length_GM_radius_of_curvature_first",
    )
    def _compute_left_ocular_axial_length_GM_radius_of_curvature_third(self):
        for rec in self:
            if rec.left_eye_steep_or_flat_k_mm_third == 0:
                rec.left_ocular_axial_length_GM_radius_of_curvature_third = 0
            else:
                rec.left_ocular_axial_length_GM_radius_of_curvature_third = round(
                    rec.left_eye_eyeball_axis_length
                    / rec.left_eye_steep_or_flat_k_mm_third,
                    3,
                )

    @api.depends(
        "left_eye_steep_or_flat_k_mm_second", "left_eye_steep_or_flat_k_mm_first"
    )
    def _compute_left_eye_steep_or_flat_k_mm_third(self):
        for rec in self:
            rec.left_eye_steep_or_flat_k_mm_third = ZResearchUtils.sum_if_num(
                rec.left_eye_steep_or_flat_k_mm_second,
                rec.left_eye_steep_or_flat_k_mm_first,
            )

    @api.depends(
        "right_eye_objective_anterior_refraction_first",
        "right_eye_objective_paralytic_refraction_first",
    )
    def _compute_pre_myopia_refractive_error_right_eye_value(self):
        for rec in self:
            rec.pre_myopia_refractive_error_right_eye_value = (
                ZResearchUtils.compute_myopia_refractive_error__value(
                    rec.right_eye_objective_anterior_refraction_first,
                    rec.right_eye_objective_paralytic_refraction_first,
                )
            )

    @api.depends(
        "left_eye_objective_anterior_refraction_first",
        "left_eye_objective_paralytic_refraction_first",
    )
    def _compute_pre_myopia_refractive_error_left_eye_value(self):
        for rec in self:
            rec.pre_myopia_refractive_error_left_eye_value = (
                ZResearchUtils.compute_myopia_refractive_error__value(
                    rec.left_eye_objective_anterior_refraction_first,
                    rec.left_eye_objective_paralytic_refraction_first,
                )
            )

    @api.onchange("right_eye_objective_anterior_refraction_first")
    def onchange_right_eye_objective_anterior_refraction_first(self):
        ZResearchUtils.check_pl_or_number(
            self.right_eye_objective_anterior_refraction_first
        )

    @api.onchange("left_eye_objective_anterior_refraction_first")
    def onchange_left_eye_objective_anterior_refraction_first(self):
        ZResearchUtils.check_pl_or_number(
            self.left_eye_objective_anterior_refraction_first
        )

    @api.onchange("right_eye_objective_paralytic_refraction_first")
    def onchange_right_eye_objective_paralytic_refraction_first(self):
        ZResearchUtils.check_pl_or_number(
            self.right_eye_objective_paralytic_refraction_first
        )

    @api.onchange("left_eye_objective_paralytic_refraction_first")
    def onchange_left_eye_objective_paralytic_refraction_first(self):
        ZResearchUtils.check_pl_or_number(
            self.left_eye_objective_paralytic_refraction_first
        )

    @api.depends(
        "right_eye_eyeball_axis_length",
        "family_history_of_myopia",
        "pre_myopia_refractive_error_right_eye_point",
    )
    def _compute_right_eye_classification(self):
        for rec in self:

            if (
                rec.right_eye_eyeball_axis_length != 0
                and rec.family_history_of_myopia != False
                and rec.pre_myopia_refractive_error_right_eye_point != False
            ):
                total_point = (
                    float(rec.right_eyeball_axis_length_point)
                    + float(rec.family_history_of_myopia_point)
                    + float(rec.pre_myopia_refractive_error_right_eye_point)
                )
                if total_point == 0:
                    rec.right_eye_classification = _("Very low/ None")
                elif 1 <= total_point <= 3:
                    rec.right_eye_classification = _("Low risk")
                elif 4 <= total_point <= 6:
                    rec.right_eye_classification = _("Medium risk")
                elif 7 <= total_point <= 10:
                    rec.right_eye_classification = _("High risk")
            else:
                rec.right_eye_classification = _("Insufficient Classification data")

    @api.depends(
        "left_eye_eyeball_axis_length",
        "family_history_of_myopia",
        "pre_myopia_refractive_error_left_eye_point",
    )
    def _compute_left_eye_classification(self):
        for rec in self:
            if (
                rec.left_eye_eyeball_axis_length != 0
                and rec.family_history_of_myopia != False
                and rec.pre_myopia_refractive_error_left_eye_point != False
            ):
                total_point = (
                    float(rec.left_eyeball_axis_length_point)
                    + float(rec.family_history_of_myopia_point)
                    + float(rec.pre_myopia_refractive_error_left_eye_point)
                )
                if total_point == 0:
                    rec.left_eye_classification = _("Very low/ None")
                elif 1 <= total_point <= 3:
                    rec.left_eye_classification = _("Low risk")
                elif 4 <= total_point <= 6:
                    rec.left_eye_classification = _("Medium risk")
                elif 7 <= total_point <= 10:
                    rec.left_eye_classification = _("High risk")
            else:
                rec.left_eye_classification = _("Insufficient Classification data")

    @api.depends("pre_myopia_refractive_error_right_eye_value")
    def _compute_pre_myopia_refractive_error_right_eye_point(self):
        for rec in self:
            rec.pre_myopia_refractive_error_right_eye_point = (
                ZResearchUtils.compute_pre_myopia_refractive_error_right_eye_point(
                    rec.pre_myopia_refractive_error_right_eye_value,
                    rec.right_eye_objective_paralytic_refraction_first,
                    rec.right_eye_objective_anterior_refraction_first,
                    rec.customer_age,
                )
            )

    @api.depends("pre_myopia_refractive_error_left_eye_value")
    def _compute_pre_myopia_refractive_error_left_eye_point(self):
        for rec in self:
            rec.pre_myopia_refractive_error_left_eye_point = (
                ZResearchUtils.compute_pre_myopia_refractive_error_right_eye_point(
                    rec.pre_myopia_refractive_error_left_eye_value,
                    rec.left_eye_objective_paralytic_refraction_first,
                    rec.left_eye_objective_anterior_refraction_first,
                    rec.customer_age,
                )
            )

    @api.depends("family_history_of_myopia")
    def _compute_history_of_myopia_point(self):
        for rec in self:
            compute = ZResearchUtils.compute_score_family_history_of_myopia(
                rec.family_history_of_myopia, rec.customer_age
            )
            rec.family_history_of_myopia_point = compute[0]
            rec.family_history_of_myopia_value = compute[1]

    def action_print(self):
        action = self.env["ir.actions.report"]._for_xml_id(
            "z_ophthalmology.action_report_comprehensive"
        )
        return action

    def check_empty_biometrics_fields(self, values):
        if self.is_valid_for_research:
            right_eye_steep_or_flat_k_first = values.get(
                "right_eye_steep_or_flat_k_first"
            )
            right_eye_steep_or_flat_k_second = values.get(
                "right_eye_steep_or_flat_k_second"
            )
            left_eye_steep_or_flat_k_first = values.get(
                "left_eye_steep_or_flat_k_first"
            )
            left_eye_steep_or_flat_k_second = values.get(
                "left_eye_steep_or_flat_k_second"
            )

            biometrics_values = [
                right_eye_steep_or_flat_k_first,
                right_eye_steep_or_flat_k_second,
                left_eye_steep_or_flat_k_first,
                left_eye_steep_or_flat_k_second,
            ]

            for value in biometrics_values:
                if value in ("0", ""):
                    raise ValidationError(_("Biometrics field must not be 0 or empty."))

            if self.left_eye_classification == _(
                "Insufficient Classification data"
            ) or self.right_eye_classification == _("Insufficient Classification data"):
                raise ValidationError(_("Must be complete research field"))

    def create(self, value):
        try:
            record = super(ZComprehensive, self).create(value)
            return record
        except ValueError:
            raise ValidationError(_("Maybe Wrong"))

    def write(self, values):
        try:
            result = super(ZComprehensive, self).write(values)
            return result
        except ValueError:
            raise ValidationError(_("Maybe Wrong"))
