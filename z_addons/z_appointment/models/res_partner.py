# -*- coding: utf-8 -*-

from odoo import models, fields


class ZPartner(models.Model):
    _inherit = "res.partner"

    visit_ids = fields.One2many(
        string="Visits",
        comodel_name="z_appointment.appointment",
        inverse_name="customer_id",
    )
    # past_illness = fields.Text("Past Illness") # Bệnh trong quá khứ
    # surgery = fields.Text("Surgery") # Phẫu thuật
    # illness_of_a_family_member = fields.Text("Illness of a family member") # Bệnh của thành viên gia đình
    # current_illness = fields.Text("Current illness") # Bệnh hiện tại
    # other_medical_history = fields.Text("Other medical history") # Bệnh sử khác
    # allergy = fields.Text("Allergy") # Dị ứng
