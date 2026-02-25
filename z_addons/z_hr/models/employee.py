# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.z_hr.helpers.constants import HrErrorCode
from odoo.addons.z_web.helpers.model_utils import ZModelUtils
from odoo.addons.z_web.helpers.validation import ZValidation
from odoo.addons.z_hr.helpers.time_slot_utils import ZTimeSlotUtils


class ZEmployee(models.Model):
    _inherit = ["hr.employee"]

    code = fields.Char(string="Employee code", readonly=True, compute="_compute_code")
    bookable = fields.Boolean("Bookable", related="job_id.bookable", tracking=True)
    is_doctor = fields.Boolean("Is doctor", related="job_id.is_doctor", tracking=True)
    gender = fields.Selection(default="male", required=True)
    birthday = fields.Date(required=True)
    mobile_phone = fields.Char(required=True, unaccent=False)
    place_ids = fields.Many2many(
        "z_place.place", string="Places", tracking=True, required=True
    )
    job_id = fields.Many2one(required=True)
    resource_calendar_employee_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Calendar",
        compute="_compute_resource_calendar_id",
    )

    @api.depends()
    def _compute_resource_calendar_id(self):
        for record in self:
            record.resource_calendar_employee_id = (
                self.env["resource.calendar"]
                .search([("employee_id", "=", record.id)], limit=1)
                .id
                or False
            )

    @api.depends()
    def _compute_code(self):
        for record in self:
            record.code = f"{record.company_id.code}{record.id:06d}"

    @api.constrains("birthday")
    def check_hours(self):
        for record in self:
            if record.birthday:
                ZValidation.validate_dob(record.birthday)

    @api.constrains("mobile_phone")
    def check_mobile(self):
        for record in self:
            if record.mobile_phone:
                ZValidation.validate_phone_number(record.mobile_phone)

    @api.constrains("company_id")
    def check_company_id(self):
        for record in self:
            if record.company_id and not record.company_id.code:
                raise ValidationError(_("Please set up a company code"))

    @api.constrains("name", "birthday", "mobile_phone", "gender")
    def _check_unique_info(self):
        for rec in self:
            if (
                len(
                    self.search(
                        [
                            ("name", "=", rec.name),
                            ("birthday", "=", rec.birthday),
                            ("mobile_phone", "=", rec.mobile_phone),
                            ("gender", "=", rec.gender),
                        ]
                    )
                )
                > 1
            ):
                raise ValidationError(
                    _(
                        "The employee information is duplicated in the system. Please try again."
                    )
                )

    def _get_employee_by_id(self, employee_id):
        return ZModelUtils.get_record_by_id(
            self, employee_id, HrErrorCode.EMPLOYEE_DOES_NOT_EXIST
        )

    def write(self, values):
        list_fields = ["place_ids", "job_id"]

        if not any(fields in values for fields in list_fields):
            return super().write(values)

        new_job_id = self.env["hr.job"].search([("id", "=", values.get("job_id"))])
        old_job_id = self.job_id
        calendar_id = self.env["resource.calendar"].search(
            [("employee_id", "=", self.id)]
        )
        old_place_ids = self.place_ids.ids
        attendance_ids = calendar_id.attendance_ids.ids if calendar_id else False
        booked_place_ids = set(calendar_id.attendance_ids.mapped("place_id").ids)

        if any(fields in values for fields in list_fields):
            if new_job_id:
                # if new_job_id.bookable == old_job_id.bookable:
                #     self.env[
                #         "z_hr.time_slot"
                #     ].raise_error_if_has_future_booked_time_slots_employee(
                #         attendance_ids
                #     )
                if old_job_id.bookable and not new_job_id.bookable:
                    if attendance_ids:
                        # self.env[
                        #     "z_hr.time_slot"
                        # ].raise_error_if_has_future_booked_time_slots_employee(
                        #     attendance_ids
                        # )
                        ZTimeSlotUtils.delete_old_time_slots_by_attendances(
                            calendar_id, self.id, attendance_ids
                        )
                else:
                    if attendance_ids:
                        updated_attendance_ids = []
                        new_attendances = self.env[
                            "resource.calendar.attendance"
                        ].get_resource_calendar_attendances_by_ids(attendance_ids)

                        ZTimeSlotUtils.change_time_slots_after_change_resource_attendances_async(
                            calendar_id,
                            self.id,
                            updated_attendance_ids,
                            new_attendances,
                        )
        employee = super().write(values)
        if any(fields in values for fields in list_fields):
            new_place_ids = self.place_ids.ids
            unique_to_new = [
                item for item in old_place_ids if item not in new_place_ids
            ]
            unique_to_old = [
                item for item in new_place_ids if item not in old_place_ids
            ]
            place_items = unique_to_new + unique_to_old
            if any(place in booked_place_ids for place in place_items):
                raise ValidationError(
                    _("It is not possible to update place with future appointments")
                )
        return employee

    def _format_mobile(self):
        if self.mobile_phone:
            self.mobile_phone = (
                self._phone_format(fname="mobile_phone", force_format="INTERNATIONAL")
                or self.mobile_phone
            )
