# -*- coding: utf-8 -*-

from typing import List
from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_hr.helpers.constants import HrErrorCode


class ZTimeSlot(models.Model):
    _name = "z_hr.time_slot"
    _description = "time slot"

    employee_id = fields.Many2one("hr.employee", "time_slot_id", ondelete="cascade")
    attendance_id = fields.Many2one(
        "resource.calendar.attendance", "time_slot_id", ondelete="cascade"
    )
    start_time = fields.Datetime(string="Start time")
    slot_size = fields.Integer(string="Slot size")
    enable = fields.Boolean(string="Enable", default=True)
    booked = fields.Boolean(string="Booked", default=False)
    place_id = fields.Many2one(
        "z_place.place", string="Place", related="attendance_id.place_id", store=True
    )
    # note: delete constraints unique field start_time
    _sql_constraints = []

    def init(self):
        self._cr.execute(
            "ALTER TABLE z_hr_time_slot DROP CONSTRAINT IF EXISTS employee_start_time_unique;"
        )

    def _get_enable_time_slot_by_id(self, time_slot_id: int, old_slot=False):
        search_domain = [("id", "=", time_slot_id), ("enable", "=", True)]
        if not old_slot:
            search_domain.append(("start_time", ">=", ZUtils.now()))
        record = self.search(search_domain, limit=1)
        if not record:
            raise UserError(HrErrorCode.TIME_SLOT_IS_DISABLE)
        return record

    def get_future_time_slots_by_employee_id(self, employee_id):
        return self.search(
            [
                ("employee_id", "=", employee_id),
                ("start_time", ">=", ZUtils.now()),
            ]
        )

    def _get_future_booked_time_slots_by_employee_id(self, employee_id: int):
        return self.search(
            [
                ("employee_id", "=", employee_id),
                ("start_time", ">=", ZUtils.now()),
                ("booked", "=", True),
            ]
        )

    def raise_error_if_employee_has_future_booked_time_slots(self, employee_id: int):
        if self._get_future_booked_time_slots_by_employee_id(employee_id):
            raise ValidationError(
                _(
                    "It is not possible to change resource calendar for employee who has future appointment"
                )
            )

    def _get_future_booked_time_slots_by_attendances(self, attendance_ids):
        return self.search(
            [
                ("attendance_id", "in", attendance_ids),
                ("start_time", ">=", ZUtils.now()),
                ("booked", "=", True),
            ]
        )

    def raise_error_if_has_future_booked_time_slots(self, attendance_ids: List[int]):
        if self._get_future_booked_time_slots_by_attendances(attendance_ids):
            raise ValidationError(
                _("It is not possible to update attendances with future appointments")
            )

    def raise_error_if_has_future_booked_time_slots_employee(
        self, attendance_ids: List[int]
    ):
        if self._get_future_booked_time_slots_by_attendances(attendance_ids):
            raise ValidationError(
                _("It is not possible to update job with future appointments")
            )

    def raise_error_if_has_future_booked_time_slots_place(
        self, attendance_ids: List[int]
    ):
        if self._get_future_booked_time_slots_by_attendances(attendance_ids):
            raise ValidationError(
                _("It is not possible to update place with future appointments")
            )

    def _get_time_slots_by_employee_ids_and_start_time(
        self, employee_ids: List[int], start_time
    ):
        return self.search(
            [("employee_id", "in", employee_ids), ("start_time", "=", start_time)]
        )
