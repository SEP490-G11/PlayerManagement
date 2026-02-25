# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons.z_web.helpers.validation import ZValidation
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.exceptions import UserError, ValidationError
from odoo.addons.z_partner.helpers.constants import (
    PartnerErrorCode,
    CUSTOMER_RECORD_LIMIT,
)
from datetime import date, datetime

class ZPartner(models.Model):
    _inherit = "res.partner"

    gender = fields.Selection(
        [
            ("male", _("Male")),
            ("female", _("Female")),
            ("n/a", _("N/A")),
        ],
        default="female",
    )
    group_id = fields.Many2one(
        string="Group", comodel_name="z_partner.group", require=False
    )

    medical_history = fields.Text("Medical history", tracking=True)

    personnal_history = fields.Text("Personal history", tracking=True)
    mid_history = fields.Text("Medical internal disease history", tracking=True)
    med_history = fields.Text("Medical external disease history", tracking=True)
    allergy_history = fields.Text("Allergy history", tracking=True)
    family_history = fields.Text("Family history", tracking=True)
    prehistoric = fields.Text("Prehistoric", tracking=True)
    reexamination_date = fields.Date(
        string="Reexamination date",
        compute="_compute_reexamination_date",
        store=True
    )
    contact_source = fields.Selection(
        [
            ("1", _("Facebook")),
            ("2", _("Hotline")),
            ("3", _("Zalo")),
            ("4", _("Website")),
            ("5", _("Tiktok")),
            ("6", _("Instagram")),
            ("7", _("Thread")),
            ("8", _("Flyer")),
            ("9", _("Standee")),
            ("10", _("Self-coming")),
            ("11", _("Other")),
        ],
        default="1",
        required=False,
        string="Contact source",
    )
    appointment_ids = fields.One2many(
        string="Appointments",
        comodel_name="z_appointment.appointment",
        inverse_name="customer_id",
    )

    def _validate_data(self, data):
        required_fields = ["name", "gender", "mobile"]
        ZValidation.validate_required_field(data, required_fields)
        ZValidation.validate_phone_number(data["mobile"])
        if data["date"]:
            ZValidation.validate_dob(data["date"])
        return ZUtils.strip_values(data)

    @api.model_create_multi
    def create(self, values):
        for value in values:
            is_customer = value.get("is_customer", False)
            if is_customer:
                if (
                        self.search_count([("is_customer", "=", True)])
                        >= CUSTOMER_RECORD_LIMIT
                ):
                    raise UserError(PartnerErrorCode.CUSTOMER_QUANTITY_LIMIT_EXCEEDED)

                value = self._validate_data(value)
                if "group_id" in value:
                    group_record = self.env["z_partner.group"]._get_group_by_id(value["group_id"])
                    if not group_record:
                        value["group_id"] = False
                else:
                    value["group_id"] = False

            domain = [
                ("name", "=", value["name"]),
            ]
            if value.get("date"):
                domain.append(("date", "=", value["date"]))
            if value.get("gender"):
                domain.append(("gender", "=", value["gender"]))
            if value.get("mobile"):
                domain.append(("mobile", "=", value["mobile"]))

            # if len(self.search(domain)) > 0:
            #     raise ValidationError(
            #         _(
            #             "The customer information is duplicated in the system. Please try again."
            #         )
            #     )
        partners = super().create(values)
        for partner in partners:
            partner._format_mobile()
            if partner.is_customer:
                partner.code = f"KH{partner.id:06d}"
        return partners
    
    @api.depends("appointment_ids", "appointment_ids.general_result_ids.reexamination_date")
    def _compute_reexamination_date(self):
        for record in self:
            all_dates = (
                    record.appointment_ids.mapped('general_result_ids.reexamination_date')
            )
            valid_dates = []
            for date_exam in all_dates:
                if isinstance(date_exam, str) and date_exam > date.today():
                    try:
                        date_exam = datetime.strptime(date_exam, "%Y-%m-%d").date()
                        if date_exam > date.today():
                            valid_dates.append(date_exam)
                    except ValueError:
                        continue
                elif isinstance(date_exam, date) and date_exam > date.today():
                    valid_dates.append(date_exam)
            if valid_dates:
                record.reexamination_date = min(valid_dates)
            else:
                record.reexamination_date = False