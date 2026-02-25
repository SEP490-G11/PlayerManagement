# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ZEmployee(models.Model):
    _inherit = "hr.employee"

    def unlink(self):
        for rec in self:
            appointment = self.env["z_appointment.appointment"].search(
                ["|", ("doctor_id", "=", rec.id), ("technician_id", "=", rec.id)],
                limit=1,
            )
            if appointment:
                raise ValidationError(
                    _("Have a appointment which assigned to this employee")
                )

            return super().unlink()
