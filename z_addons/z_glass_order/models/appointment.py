# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ZAppointment(models.Model):
    _inherit = "z_appointment.appointment"

    glass_order_ids = fields.One2many(
        "z_glass_order", "visit_id", "Glass Order", copy=True
    )
    has_glass_order = fields.Boolean(
        string="Has Glass Order", compute="_compute_has_glass_order", store=False
    )

    @api.depends("glass_order_ids")
    def _compute_has_glass_order(self):
        for rec in self:
            rec.has_glass_order = len(rec.glass_order_ids) > 0

    def action_open_glass_order_form(self):  
        if int(self.state) == 1:
            raise ValidationError("Trạng thái 'Chưa đến' không thể tạo đơn kính")
        glass_order = self.env["z_glass_order"].search(
            [("visit_id", "=", self.id)], limit=1
        )
        if glass_order:
            return {
                "type": "ir.actions.act_window",
                "name": "Đơn kính",
                "view_mode": "form",
                "res_model": "z_glass_order",
                "res_id": glass_order.id,
                "context": {},
                "target": "current",
            }
        else:
            comprehensive = self.env["z_ophthalmology.comprehensive"].search(
                [("visit_id", "=", self.id)], limit=1
            )
            if comprehensive:
                return {
                    "type": "ir.actions.act_window",
                    "name": "Đơn kính",
                    "view_mode": "form",
                    "res_model": "z_glass_order",
                    "res_id": None,
                    "context": {
                        "default_customer_id": self.customer_id.id,
                        "default_examination_date": self.time_slot_start_time.date(),
                        "default_visit_id": self.id,
                        "default_code": "DK",
                        "default_doctor_id": comprehensive.examiner_id.id,
                        "default_technician_id": comprehensive.optometrist_id.id,
                    },
                    "target": "current",
                }
            else:
                return {
                    "type": "ir.actions.act_window",
                    "name": "Đơn kính",
                    "view_mode": "form",
                    "res_model": "z_glass_order",
                    "res_id": None,
                    "context": {
                        "default_customer_id": self.customer_id.id,
                        "default_examination_date": self.time_slot_start_time.date(),
                        "default_visit_id": self.id,
                        "default_code": "DK",
                        "default_doctor_id": self.doctor_id.id,
                        "default_technician_id": self.technician_id.id,
                    },
                    "target": "current",
                }
