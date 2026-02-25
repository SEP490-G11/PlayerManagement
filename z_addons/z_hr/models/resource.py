# -*- coding: utf-8 -*-

from odoo import fields, models


class ZResourceResource(models.Model):
    _inherit = "resource.resource"

    user_id = fields.Many2one(required=False)

    def _get_bookable_resource_by_resource_calendar(self, resource_calendar_id):
        return self.search(
            [
                ("calendar_id", "=", resource_calendar_id),
                ("employee_id.bookable", "=", True),
            ]
        )

    # def write(self, values):
    #     calendar_id = values.get("calendar_id")
    #     if (
    #         self.employee_id.bookable
    #         and calendar_id
    #         and calendar_id != self.calendar_id.id
    #     ):
    #         # Raise error if employee has future appointment
    #         self.env[
    #             "z_hr.time_slot"
    #         ].raise_error_if_employee_has_future_booked_time_slots(self.employee_id.id)
    #
    #         # Update resource calendar
    #         self.env["resource.calendar"].update_resource_calendar(
    #             calendar_id,
    #             self.employee_id.id,
    #             self.calendar_id.attendance_ids.mapped("id"),
    #         )
    #     return super().write(values)
