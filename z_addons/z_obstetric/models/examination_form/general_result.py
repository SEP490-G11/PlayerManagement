# -*- coding: utf-8 -*-

from unidecode import unidecode
from odoo import models, fields, api, _


class ZGeneralResult(models.Model):
    _name = "z_obstetric.general_result"
    _inherit = ["z_medical_record.medical_result", "mail.thread", "mail.activity.mixin"]
    _description = "General result"

    blood_pressure = fields.Text("Blood Pressure")
    pulse = fields.Text("Pulse")  # Mạch
    cardiopulmonary = fields.Text("Cardiopulmonary")  # Tim phổi
    weight = fields.Text("Weight")
    product_service_ids = fields.One2many(
        "z_medical_record.service", "general_result_id", "Service", copy=True
    )  # Thủ thuật
    product_drug_ids = fields.One2many(
        "z_medical_record.drug", "general_result_id", "Prescription", copy=True
    )  # Thuốc
    # Chuẩn đoán - Mã bệnh
    allergy = fields.Text("Allergy")  # Dị ứng
    disease_history = fields.Text(
        "Medical History",
        compute="_compute_all_history",
        store=True,
        readonly=False,
        tracking=True,
    )  # Bệnh sử
    other_diagnose = fields.Text("Other Diagnose")
    pdf_title = fields.Char(string="Pdf title", compute="_compute_pdf_title")
    general_result_ids = fields.One2many(
        "z_obstetric.general_result", "visit_id", "General result", copy=True
    )
    gynecological_ids = fields.One2many(
        "z_obstetric.gynecological", "visit_id", "Gynecological", copy=True
    )
    non_speculum_gynecological_ids = fields.One2many(
        "z_obstetric.non_gynecological",
        "visit_id",
        "Non Speculum Gynecological",
        copy=True,
    )
    post_first_tremester_pregnant_ids = fields.One2many(
        "z_obstetric.post_pregnant",
        "visit_id",
        "Post-first Tremester Pregnant",
        copy=True,
    )
    pre_first_tremester_pregnant_ids = fields.One2many(
        "z_obstetric.pre_pregnant",
        "visit_id",
        "Pre-first Tremester Pregnant",
        copy=True,
    )
    gyn_ult_ids = fields.One2many(
        "z_obstetric.gyn_ult",
        "visit_id",
        "Gynecological ultrasound",
        copy=True,
    )
    oval_check_idc_ids = fields.One2many(
        "z_obstetric.oval_check_idc",
        "visit_id",
        "Ovalution Checking Indicated",
        copy=True,
    )
    post_first_indicated_ids = fields.One2many(
        "z_obstetric.post_first_indicated",
        "visit_id",
        "Post first indicated",
        copy=True,
    )
    pre_first_indicated_ids = fields.One2many(
        "z_obstetric.pre_first_indicated", "visit_id", "Pre first indicated", copy=True
    )
    is_save = fields.Boolean("Is save", default=False, tracking=True)

    personnal_history = fields.Text("Personal history")
    # TODO: this field (mid_history) can use in future
    mid_history = fields.Text(
        "Medical internal disease history",
        compute="_compute_all_history",
        store=True,
        readonly=False,
        tracking=True,
    )
    # TODO: this field (med_history) can use in future
    med_history = fields.Text(
        "Medical external disease history",
        compute="_compute_all_history",
        store=True,
        readonly=False,
        tracking=True,
    )
    # TODO: this field (allergy_history) can use in future
    allergy_history = fields.Text(
        "Allergy history",
        compute="_compute_all_history",
        store=True,
        readonly=False,
        tracking=True,
    )
    # TODO: this field (family_history) can use in future
    family_history = fields.Text(
        "Family history",
        compute="_compute_all_history",
        store=True,
        readonly=False,
        tracking=True,
    )
    diagnosis = fields.Text(
        "Diagnosis",
        tracking=True,
    )
    prehistoric = fields.Text(
        "Prehistoric",
        compute="_compute_all_history",
        store=True,
        readonly=False,
        tracking=True,
    )

    @api.depends(
        "customer_id",
        "customer_id.medical_history",
        "customer_id.mid_history",
        "customer_id.med_history",
        "customer_id.allergy_history",
        "customer_id.family_history",
        "customer_id.prehistoric",
    )
    def _compute_all_history(self):
        for record in self:
            record.disease_history = (
                record.customer_id.medical_history
                if not record.disease_history
                else record.disease_history
            )
            record.mid_history = record.customer_id.mid_history
            record.med_history = record.customer_id.med_history
            record.allergy_history = record.customer_id.allergy_history
            record.family_history = record.customer_id.family_history
            record.prehistoric = (
                record.customer_id.prehistoric
                if not record.prehistoric
                else record.prehistoric
            )

    def write(self, vals):
        result = super(ZGeneralResult, self).write(vals)
        for general in self:
            if "disease_history" in vals:
                general.customer_id.write(
                    dict(medical_history=vals.get("disease_history"))
                )
            if "mid_history" in vals:
                general.customer_id.write(dict(mid_history=vals.get("mid_history")))
            if "med_history" in vals:
                general.customer_id.write(dict(med_history=vals.get("med_history")))
            if "allergy_history" in vals:
                general.customer_id.write(
                    dict(allergy_history=vals.get("allergy_history"))
                )
            if "family_history" in vals:
                general.customer_id.write(
                    dict(family_history=vals.get("family_history"))
                )
            if "prehistoric" in vals:
                general.customer_id.write(dict(prehistoric=vals.get("prehistoric")))

        return result

    @api.depends("customer_id")
    def _compute_pdf_title(self):
        for record in self:
            name = unidecode(record.customer_id.name).replace(" ", "")
            title = _("General result")
            record.pdf_title = f"{title}_{name}_{record.customer_id.code}"

    @api.model
    def create(self, vals):
        record = super(ZGeneralResult, self).create(vals)
        for general in record:
            if "prehistoric" in vals:
                general.customer_id.write(dict(prehistoric=vals.get("prehistoric")))
            if "disease_history" in vals:
                general.customer_id.write(
                    dict(medical_history=vals.get("disease_history"))
                )
        return record

    def action_print(self):
        action = self.env["ir.actions.report"]._for_xml_id(
            "z_obstetric.action_report_obstetric_general_results"
        )
        return action
