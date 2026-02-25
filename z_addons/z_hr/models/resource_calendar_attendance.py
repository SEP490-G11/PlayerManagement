# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from odoo.addons.z_hr.helpers.constants import TimeSchedule
from odoo.addons.z_web.helpers.utils import ZUtils

class ZResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    enable = fields.Boolean("Enable", default=True)
    date_from = fields.Date(string="Start Date", related="calendar_id.date_from")
    date_to = fields.Date(string="End Date", related="calendar_id.date_to")
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        related="calendar_id.employee_id",
    )

    place_id = fields.Many2one(
        string="Place",
        comodel_name="z_place.place",
        compute="_compute_place_id_by_employee",
        store=True,
        readonly=False,
    )

    # @api.constrains("place_id")
    # def check_place_id(self):
    #     for record in self:
    #         if not record.place_id:
    #             raise ValidationError(_("Place is required"))

    @api.depends("employee_id")
    def _compute_place_id_by_employee(self):
        for rec in self:
            rec.place_id = (
                rec.employee_id.place_ids[:1] if rec.employee_id.place_ids else False
            )

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

    @api.constrains("hour_from", "hour_to")
    def check_hours(self):
        start_time = ZUtils.time_to_float(TimeSchedule.FROM_TIME)
        end_time = ZUtils.time_to_float(TimeSchedule.TO_TIME)
        slot = TimeSchedule.SLOT_SIZE / 60
        for record in self:
            # TODO: this can be reuse in the future
            # if record.hour_from < start_time or record.hour_to > end_time:
            #     raise ValidationError(_("Outside the clinic's working hours"))
            if (record.hour_to - record.hour_from) < slot:
                raise ValidationError(
                    _("The end time must be greater than the start time at least")
                    + f" {TimeSchedule.SLOT_SIZE} "
                    + _("minutes")
                )

    def get_resource_calendar_attendances_by_ids(self, ids):
        return self.search([("id", "in", ids)])

    @api.onchange("hour_from", "hour_to")
    def _onchange_hour_field(self):
        appointments = self.env["z_appointment.appointment"].search(
        [
            "|",
            ("doctor_id", "=", self.employee_id[0].id),
            ("technician_id", "=", self.employee_id[0].id),
            ("time_slot_id.attendance_id", "=", self._origin.id),
        ])
        if(len(appointments) > 0):
            self.env.user.notify_warning(
                    message=_("There are appointments booked for this time!"),
                    title=_("Warning:"), 
                    sticky=False
                )
