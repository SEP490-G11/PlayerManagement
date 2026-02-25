# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta


class ZAppointment(models.Model):
    _inherit = "z_appointment.appointment"

    customer_age = fields.Integer(
        string="Customer Age", related="customer_id.age", store=True
    )

    retell_datetime = fields.Datetime(
        string="Retell Datetime", compute="_compute_retell_datetime", store=True
    )

    @api.depends("booking_date")
    def _compute_retell_datetime(self):
        for appointment in self:
            retell_datetime = False
            if appointment.booking_date:
                retell_datetime = datetime.combine(
                    appointment.booking_date, datetime.min.time()
                ).replace(hour=0, minute=0, second=0) - timedelta(days=2)
                retell_datetime = retell_datetime.replace(hour=10, minute=0, second=0)

            else:
                retell_datetime = False
            appointment.retell_datetime = retell_datetime
            
    def unlink(self):
        for record in self:
            queues = self.env["z.crm.zns.template.queue"].search([("crm_queue_id.model_name","=","z_appointment.appointment"),("crm_queue_id.record_id","=",record.id)])
            for queue in queues:
                    queue.crm_queue_id.unlink()
        return  super().unlink()
        
class ZComboOrder(models.Model):
    _inherit = "z_combo.combo.order"

    customer_age = fields.Integer(
        string="Customer Age", related="customer_id.age", store=True
    )
