# -*- coding: utf-8 -*-
from typing import List
from odoo import fields, models, api, _
from odoo.addons.z_web.helpers.model_utils import ZModelUtils
from odoo.addons.z_hr.helpers.time_slot_utils import ZTimeSlotUtils
from odoo.exceptions import ValidationError
from odoo.addons.z_hr.helpers.constants import TimeSchedule
from datetime import date


class ZResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    # def unlink(self):
    #     for rec in self:
    #         appointment = self.env["z_appointment.appointment"].search(
    #             [
    #                 "|",
    #                 ("doctor_id", "=", rec.employee_id.id),
    #                 ("technician_id", "=", rec.employee_id.id),
    #             ]
    #         )
    #         if appointment:
    #             raise ValidationError(
    #                 _("You cannot delete a calendar that has placed employee.")
    #             )
    #     return super(ZResourceCalendar, self).unlink()
