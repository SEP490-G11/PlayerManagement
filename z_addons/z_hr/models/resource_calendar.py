# -*- coding: utf-8 -*-
from typing import List
from odoo import fields, models, api, _
from odoo.addons.z_web.helpers.model_utils import ZModelUtils
from odoo.addons.z_hr.helpers.time_slot_utils import ZTimeSlotUtils
from odoo.exceptions import ValidationError
from odoo.addons.z_hr.helpers.constants import TimeSchedule
from datetime import date, datetime
from odoo.addons.z_web.helpers.utils import ZUtils

class ZResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    tz = fields.Selection(default=lambda self: self.env.user.tz or "UTC")
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        required=True,
        domain="['|','&', ('id', 'not in', existing_employee_ids), ('is_doctor', '=', True),'&', ('id', 'not in', existing_employee_ids), ('bookable', '=', True)]",
    )

    existing_employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        compute="_compute_existing_employee_ids",
        store=False,
    )

    is_template = fields.Boolean(string="Template lock", default=False)
    is_admin = fields.Boolean(string="Template lock", compute="_compute_is_admin")
    is_edited = fields.Integer(string="Is Editing", default=1)

    @api.depends()
    def _compute_is_admin(self):
        for rec in self:
            rec.is_admin = (
                True
                if rec.id == 1 and self.env.user.has_group("base.group_system")
                else False
            )

    @api.depends("employee_id")
    def _compute_existing_employee_ids(self):
        # Get all the employees already assigned to resource calendars
        assigned_employee_ids = self.search([]).mapped("employee_id.id")
        for record in self:
            record.existing_employee_ids = [(6, 0, assigned_employee_ids)]

    employee_place_ids = fields.Many2many(
        string="Place of Employee",
        comodel_name="z_place.place",
        related="employee_id.place_ids",
    )
    date_from = fields.Date(string="Starting Date", required=True)
    date_to = fields.Date(string="End Date", required=True)

    @api.constrains("date_from", "date_to")
    def check_dates(self):
        current_date = date.today()
        for record in self:
            if not record.date_from or not record.date_to:
                raise ValidationError(_("Start date and end date are required"))
            if record.date_from and record.date_from < current_date:
                raise ValidationError(
                    _("The start date must be later than current date.")
                )
            if record.date_from > record.date_to:
                raise ValidationError(
                    _("The start date must be earlier than the end date.")
                )
            if (abs(record.date_to - record.date_from)).days > TimeSchedule.MAX_DAYS:
                raise ValidationError(
                    _("Work schedules can only be created within 60 days")
                )

    def _get_resource_calendar_by_id(self, id):
        return ZModelUtils.get_record_by_id(self, id)

    def _get_resource_calendar_by_ids(self, ids):
        return self.search([("id", "in", ids)])

    # def update_resource_calendar(
    #     self, new_calendar_id, employee_id: int, old_attendance_ids: List[int]
    # ):
    #     attendance_ids = self._get_resource_calendar_by_id(
    #         new_calendar_id
    #     ).attendance_ids
    #     ZTimeSlotUtils.generate_time_slots_after_change_resource_calendar_for_employee_async(
    #         self, employee_id, attendance_ids, old_attendance_ids
    #     )

    def create(self, values):
        calendar = super().create(values)
        self.env.cr.commit()

        employee_id = calendar.employee_id
        if employee_id.bookable:
            attendance_ids = calendar.attendance_ids.ids
            updated_attendance_ids = []

            new_attendances = self.env[
                "resource.calendar.attendance"
            ].get_resource_calendar_attendances_by_ids(attendance_ids)

            ZTimeSlotUtils.change_time_slots_after_change_resource_attendances_async(
                self, employee_id.id, updated_attendance_ids, new_attendances
            )
        return calendar

    def write(self, values):
        attendance_ids = values.get("attendance_ids")
        employee_id = values.get("employee_id")
        date_from = values.get("date_from") 
        date_to = values.get("date_to")

        # Handle date range update
        if date_from or date_to:
            calendar = super().write(values)
            self.env.cr.commit()
            attendance_ids = self.attendance_ids

        # Handle employee update
        if employee_id:
            updated_attendance_ids = self.attendance_ids.ids
            ZTimeSlotUtils.delete_old_time_slots_by_attendances(
                self, self.employee_id.id, updated_attendance_ids
            )

        if not attendance_ids and not employee_id:
            return super().write(values)

        # Fields affecting the attendance records
        effect_fields = [
            "day_period",
            "date_from",
            "date_to",
            "hour_from",
            "hour_to",
            "enable",
            "place_id",
        ]

        # Collect updated attendance IDs
        updated_attendance_ids = [
            i[1]
            for i in attendance_ids
            if i[0] == 1 and any(k in effect_fields for k in i[2])
        ]

        # Saving process
        current_attendance_ids = self.attendance_ids
        calendar = super().write(values)
        self.env.cr.commit()
        created_attendances = self.attendance_ids - current_attendance_ids
        employee_id = self.employee_id

        # If date range is updated, update attendance IDs
        if date_from or date_to:
            updated_attendance_ids = self.attendance_ids.ids
            created_attendances = self.attendance_ids

        # Handle bookable employee
        if employee_id.bookable:
            if created_attendances or updated_attendance_ids:
                created_ids = created_attendances.mapped("id") + updated_attendance_ids
                new_attendances = self.env[
                    "resource.calendar.attendance"
                ].get_resource_calendar_attendances_by_ids(created_ids)
                ZTimeSlotUtils.change_time_slots_after_change_resource_attendances_async(
                    self, employee_id.id, updated_attendance_ids, new_attendances
                )
        return calendar            

    @api.onchange("attendance_ids")
    def check_valid_input_hours_attendance_ids(self):
        for current_attendance in self.attendance_ids:
            # Check if there is another attendance with the same dayofweek and different ID
            for other_attendance in self.attendance_ids:
                if current_attendance.dayofweek == other_attendance.dayofweek and str(
                    current_attendance.id
                ) != str(other_attendance.id):

                    # Check for overlap
                    if (
                        current_attendance.hour_to
                        > other_attendance.hour_from
                        >= current_attendance.hour_from
                    ) or (
                        other_attendance.hour_to
                        > current_attendance.hour_from
                        >= other_attendance.hour_from
                    ):
                        raise ValidationError(_("Invalid time range!"))

    def unlink(self):
        for rec in self:
            time_slot_past = self.env["z_hr.time_slot"].search(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("booked", "=", True),
                    ("start_time", "<=", ZUtils.now()),
                ]
            )
            time_slot_future = self.env["z_hr.time_slot"].search(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("booked", "=", True),
                    ("start_time", ">", ZUtils.now()),
                ]
            )
            if time_slot_future:
                raise ValidationError(
                    _("You cannot delete a calendar that has booked slots")
                )
            if time_slot_past:
                raise ValidationError(
                    _(
                        "You cannot delete a calendar that has booked slots, please archive it"
                    )
                )

        return super(ZResourceCalendar, self).unlink()

    def action_open_message_warning_calendar_form(self, date_from_origin):
        wizard = self.env['resource.calendar.change.wizard'].create({
            'doctor_id': self.employee_id[0].id,
            'date_from_origin': date_from_origin
        })
        return {
            "type": "ir.actions.act_window",
            "name": _("Message Warning Calendar Change"),
            "view_mode": "form",
            "res_model": "resource.calendar.change.wizard",
            "res_id": wizard.id,
            "target": "new",
            "views": [
                (self.env.ref("z_hr.view_resource_calendar_change_wizard").id, "form")
            ],
            "context": self.env.context
        }
    
    @api.onchange("date_from", "date_to")
    def _onchange_date_field(self):
        # format date to m/d/y h:m to compare
        if(self.date_from):
            current_time = datetime.now()
            formatted_time_current = current_time.strftime("%m/%d/%Y %H:%M")
            if self.date_from and self.date_to:
                date_obj_time_from = datetime.combine(self.date_from, datetime.min.time())
                date_obj_time_to = datetime.combine(self.date_to, datetime.min.time())
                formatted_time_from = date_obj_time_from.strftime("%m/%d/%Y 00:00")
                formatted_time_to = date_obj_time_to.strftime("%m/%d/%Y 00:00")
                # check date_from with time now
                if(formatted_time_from > formatted_time_current):
                    # check appointments of doctor have not been examined
                    appointments = self.env["z_appointment.appointment"].search(
                        [
                            "|",
                            "&",
                            ("time_slot_id.start_time", ">=", formatted_time_current),
                            ("time_slot_id.start_time", "<=", formatted_time_from),
                            "&",
                            ("time_slot_id.start_time", ">=", formatted_time_from),
                            ("time_slot_id.start_time", "<=", formatted_time_to),
                            "|",
                            ("doctor_id", "=", self.employee_id[0].id),
                            ("technician_id", "=", self.employee_id[0].id),
                        ]
                    )
                    if len(appointments) > 0:
                        self.env.user.notify_warning(
                            message=_("There are appointments booked for this time!"),
                            title=_("Warning:"), 
                            sticky=False
                        )

    def read(self, fields, load):
        res = super(ZResourceCalendar, self).read(fields=fields, load=load)
        for record in res:
            # set status form edited
            record_id = record.get('id')
            if not isinstance(record_id, int):
                record['is_edited'] = 0
            else:
                record['is_edited'] = 1
        return res
