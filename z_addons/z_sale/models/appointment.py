# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ZAppointment(models.Model):
    _inherit = "z_appointment.appointment"
    _order = "booking_date desc, get_examination_code desc"

    sale_order_ids = fields.One2many(
        "sale.order",
        "z_appointment_id",
        "Sale Orders",
    )

    def action_create_sale_order(self):
        if int(self.state) == 1:
            raise ValidationError("Trạng thái 'Chưa đến' không thể tạo hoá đơn'")
        return {
            "type": "ir.actions.act_window",
            "name": "Báo giá",
            "view_mode": "form",
            "res_model": "sale.order",
            "res_id": None,
            "id": self.env.ref("z_sale.z_sale_order_form_view").id,
            "context": {
                "default_z_appointment_id": self.id,
                "default_partner_id": self.customer_id.id,
                "default_company_id": self.env.company.id,
                "linked_from_appointment": True,
            },
            "target": "current",
        }
