# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class ZSaleOrder(models.Model):
    _inherit = "sale.order"
    
    z_appointment_id = fields.Many2one(
        "z_appointment.appointment", string="Appointment"
    )
    
    partner_name = fields.Char(
        string="Partner name", compute="_compute_partner_name", store=True
    )
    partner_fullname = fields.Char(
        string="Full name", related="partner_id.name", store=True
    )
    partner_group = fields.Char(string="Group", related="partner_id.group_id.name")
    partner_code = fields.Char(string="Partner code", related="partner_id.code")
    partner_gender = fields.Selection(string="Gender", related="partner_id.gender")
    partner_dob = fields.Date(
        string="Date of birth", related="partner_id.date", default=False
    )
    partner_mobile = fields.Char(string="Phone number", related="partner_id.mobile")
    partner_z_mobile = fields.Char(string="Phone number", related="partner_id.z_mobile")
    partner_job = fields.Char(string="Job", related="partner_id.job")
    partner_address = fields.Char(
        string="Address", related="partner_id.street", store=False
    )
    
    @api.depends("partner_id")
    def _compute_partner_name(self):
        for record in self:
            record.partner_name = record.partner_id.extra_name