# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.z_appointment.helpers.constants import (
    FLOOR_OPT_ENUM,
)

class ZAppointment(models.Model):
    _inherit = "z_appointment.appointment"
    
    floor_opt = fields.Selection(
        FLOOR_OPT_ENUM, string="Floor"
    )
    comprehensive_ids = fields.One2many(
        "z_ophthalmology.comprehensive", "visit_id", "Comprehensive", copy=True
    )
    lens_ids = fields.One2many("z_ophthalmology.lens", "visit_id", "Lens", copy=True)
    re_lens_ids = fields.One2many(
        "z_ophthalmology.re_lens", "visit_id", "Re Lens", copy=True
    )
    vision_ids = fields.One2many(
        "z_ophthalmology.vision", "visit_id", "Vision", copy=True
    )
    binocular_vision_ids = fields.One2many(
        "z_ophthalmology.binocular_vision",
        "visit_id",
        "Binocular Vision",
        copy=True,
    )
    has_comprehensive = fields.Boolean(
        string="Has Comprehensive", compute="_compute_has_comprehensive", store=False
    )
    has_lens = fields.Boolean(
        string="Has lens", compute="_compute_has_lens", store=False
    )
    has_re_lens = fields.Boolean(
        string="Has re lens", compute="_compute_has_re_lens", store=False
    )
    has_vision = fields.Boolean(
        string="Has vision", compute="_compute_has_vision", store=False
    )
    has_binocular_vision = fields.Boolean(
        string="Has binocular vision",
        compute="_compute_has_binocular_vision",
        store=False,
    )

    @api.depends("comprehensive_ids")
    def _compute_has_comprehensive(self):
        for rec in self:
            rec.has_comprehensive = len(rec.comprehensive_ids) > 0

    @api.depends("lens_ids")
    def _compute_has_lens(self):
        for rec in self:
            rec.has_lens = len(rec.lens_ids) > 0

    @api.depends("re_lens_ids")
    def _compute_has_re_lens(self):
        for rec in self:
            rec.has_re_lens = len(rec.re_lens_ids) > 0

    @api.depends("vision_ids")
    def _compute_has_vision(self):
        for rec in self:
            rec.has_vision = len(rec.vision_ids) > 0

    @api.depends("binocular_vision_ids")
    def _compute_has_binocular_vision(self):
        for rec in self:
            rec.has_binocular_vision = len(rec.binocular_vision_ids) > 0

    def action_open_medical_result_form(
        self, res_model: str, name: str, examination_type: str, code: str
    ):  
        if int(self.state) == 1:
            raise ValidationError("Trạng thái 'Chưa đến' không thể tạo mẫu kết quả khám")
        medical = self.env[res_model].search([("visit_id", "=", self.id)], limit=1)
        if medical:
            return {
                "type": "ir.actions.act_window",
                "name": "Chi tiết",
                "view_mode": "form",
                "res_model": res_model,
                "res_id": medical.id,
                "target": "current",
            }
        else:
            return {
                "type": "ir.actions.act_window",
                "name": name,
                "view_mode": "form",
                "res_model": res_model,
                "res_id": None,
                "context": {
                    "default_visit_id": self.id,
                    "default_customer_id": self.customer_id.id,
                    "default_optometrist_id": self.technician_id.id,
                    "default_examiner_id": self.doctor_id.id,
                    "default_examination_date": self.time_slot_start_time.date(),
                    "default_code": code,
                    "default_customer_age": self.customer_id.age,
                    "default_examination_type": examination_type,
                    "default_customer_age": self.customer_id.age,
                },
                "target": "current",
            }

    def action_open_comprehensive_form(self):
        res_model = "z_ophthalmology.comprehensive"
        name = _("Comprehensive")
        examination_type = _("ComprehensiveType")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "EA"
        )

    def action_open_len_form(self):
        res_model = "z_ophthalmology.lens"
        name = _("Contact lens examination")
        examination_type = _("ContactLensExamination")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "EB"
        )

    def action_open_re_len_form(self):
        res_model = "z_ophthalmology.re_lens"
        name = _("Contact lens reexamination")
        examination_type = _("ContactLensReexamination")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "EB"
        )

    def action_open_vision_form(self):
        res_model = "z_ophthalmology.vision"
        name = _("Low vision examination")
        examination_type = _("VisionExamination")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "ED"
        )

    def action_open_binocular_vision_form(self):
        res_model = "z_ophthalmology.binocular_vision"
        name = _("Binocular vision examination")
        examination_type = _("BinocularVisionExamination")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "EC"
        )

    def write(self, vals):
        if vals.get("state") == "1" and (
            self.has_comprehensive
            or self.has_lens
            or self.has_re_lens
            or self.has_vision
            or self.has_binocular_vision
            or self.has_glass_order
            or self.has_invoice
        ):
            raise ValidationError(
                _("It is not possible to update the unarrived status for a visit that has already arrived")
            )
        return super().write(vals)
