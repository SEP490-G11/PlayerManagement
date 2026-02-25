# -*- coding: utf-8 -*-
import re
from datetime import date
from typing import Dict, List
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.z_partner.helpers.constants import (
    PartnerErrorCode,
    CUSTOMER_RECORD_LIMIT,
)
from odoo.addons.z_web.helpers.model_utils import ZModelUtils
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_web.helpers.validation import ZValidation

class ZPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "mail.thread", "mail.activity.mixin"]
    
    is_customer = fields.Boolean("Is customer", default=False)
    group_id = fields.Many2one(string="Group", comodel_name="z_partner.group")
    research_id = fields.Many2one(string="Research", comodel_name="z_partner.research", store=False)
    date_research = fields.Date(string="Date research", related="research_id.date", default="", store=False)
    color_research = fields.Selection(string="Color research", related="research_id.color", default="", store=False)
    code = fields.Char(string="Code", readonly=True)
    original_code = fields.Char(string="Original Code")
    age = fields.Integer(string="Age", compute="_calculate_age")
    display_age = fields.Char(
        string="Age", compute="_calculate_display_age", store=False
    )
    mobile = fields.Char(unaccent=False, string="Phone number")
    z_mobile = fields.Char(
        string="Phone number", compute="compute_z_mobile", store=True
    )
    date = fields.Date(
        index=True,
        string="Date of Birth",
        require=False,
    )
    job = fields.Char("Job")
    gender = fields.Selection(
        [
            ("male", _("Male")),
            ("female", _("Female")),
            ("n/a", _("N/A")),
        ],
        default="n/a",
    )
    extra_name = fields.Char(
        string="Extra name", compute="_compute_extra_name", store=True
    )
    customer_detail_widget = fields.Json(
        string="Customer detail", compute="_compute_customer_detail_widget"
    )
    contact_source = fields.Selection(
        [
            ("1", _("Fanpage")),
            ("2", _("Hotline")),
            ("3", _("Zalo OA")),
            ("4", _("Website")),
            ("5", _("Team")),
            ("6", _("Campain")),
            ("7", _("Facebook Ads")),
            ("8", _("Google Ads")),
            ("9", _("Come by yourself")),
            ("10", _("Screening")),
            ("11", _("Other")),
        ],
        default="1",
        required=False,
        string="Contract source",
    )
    
    approach_channel = fields.Selection([
        ('1', _('Group FB')),
        ('2', _('FB (Fanpage)')),
        ('3', _('Google')),
        ('4', _('Website')),
        ('5', _('Tiktok')),
        ('6', _('Youtube')),
        ('7', _('Referrer')),
        ('8', _('Expert page')),
        ('9', _('Self-coming'))
    ], string="Approach channel", )

    @api.depends("mobile")
    def compute_z_mobile(self):
        for record in self:
            if record.mobile:
                clean_number = re.sub(r"\D", "", record.mobile)
                if clean_number.startswith("84"):
                    record.z_mobile = f"0{clean_number[2:]}"
            else:
                record.z_mobile = False

    @api.constrains("date")
    def check_dates(self):
        for record in self:
            if record.date and record.date > date.today():
                raise ValidationError(_("Date must be earlier than current date."))

    @api.depends("date")
    def _calculate_display_age(self):
        for record in self:
            if record.date:
                record.display_age = ZUtils.calculate_age(record.date)
            else:
                record.display_age = None

    @api.constrains("name", "mobile",)
    def _check_unique_info(self):
        for rec in self:
            if (
                len(
                    self.search(
                        [
                            ("name", "=", rec.name),
                            ("mobile", "=", rec.mobile),
                        ]
                    )
                )
                > 1 and not self.env.context.get("create_employee")
            ):
                raise ValidationError(
                    _(
                        "The customer information is duplicated in the system. Please try again."
                    )
                )

    @api.depends("name", "code", "date", "gender")
    def _compute_extra_name(self):
        for record in self:
            gender = _("Male") if record.gender == "male" else _("Female")
            record.extra_name = f"{record.name}-{record.code}-{gender}-{record.date}"

    @api.depends("date")
    def _calculate_age(self):
        today = date.today()
        for record in self:
            if record.date:
                record.age = (
                    today.year
                    - record.date.year
                    - ((today.month, today.day) < (record.date.month, record.date.day))
                )
            else:
                record.age = None

    def _get_customer_by_id(self, customer_id):
        return ZModelUtils.get_record_by_id(
            self, customer_id, PartnerErrorCode.CUSTOMER_DOES_NOT_EXIST
        )

    def _format_mobile(self):
        if self.mobile:
            self.mobile = (
                self._phone_format(fname="mobile", force_format="INTERNATIONAL")
                or self.mobile
            )

    def _validate_data(self, data):
        required_fields = ["name", "group_id", "mobile"]
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
                self.env["z_partner.group"]._get_group_by_id(value["group_id"])

            domain = [
                ("name", "=", value["name"]),
            ]
            if value.get("date"):
                domain.append(("date", "=", value["date"]))
            if value.get("gender"):
                domain.append(("gender", "=", value["gender"]))
            if value.get("mobile"):
                domain.append(("mobile", "=", value["mobile"]))

            if len(self.search(domain)) > 0 and not self.env.context.get("create_employee"):
                raise ValidationError(
                    _(
                        "The customer information is duplicated in the system. Please try again."
                    )
                )
        partners = super().create(values)
        for partner in partners:
            partner._format_mobile()
            if partner.is_customer:
                partner.code = f"KH{partner.id:06d}"
        return partners

    def web_save(
        self, vals, specification: Dict[str, Dict], next_id=None
    ) -> List[Dict]:
        if self:
            if "mobile" in vals:
                ZValidation.validate_phone_number(vals["mobile"])
            self.write(vals)
        else:
            self = self.create(vals)
        if next_id:
            self = self.browse(next_id)
        return self.with_context(bin_size=True).web_read(specification)

    @api.depends("name", "code", "date", "gender")
    def _compute_display_name(self):
        if not self.env.context.get("directory_short_name", False):
            return super()._compute_display_name()
        for record in self:
            gender = _("Male") if record.gender == "male" else _("Female")
            record.display_name = f"{record.name}-{record.code}-{gender}-{record.date}"

    @api.depends()
    def _compute_customer_detail_widget(self):
        for rec in self:
            gender = {"male": _("Male"), "female": _("Female")}.get(rec.gender, "N/A")

            data = {
                "name": rec.name,
                "gender": gender,
                "age": rec.display_age,
                "code": rec.code,
                "mobile": rec.mobile,
                "address": rec.street,
                "id": rec.id,
            }
            rec.customer_detail_widget = data

    def open_customer_form(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': self.id,
            "views": [(False,'form')],
            'target': 'new'
        }