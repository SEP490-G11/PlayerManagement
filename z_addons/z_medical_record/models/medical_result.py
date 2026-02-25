# -*- coding: utf-8 -*-

from unidecode import unidecode
from odoo import models, fields, api
from datetime import datetime, timedelta


class ZMedicalResult(models.Model):
    _name = "z_medical_record.medical_result"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Medical result"
    
    visit_id = fields.Many2one(
        comodel_name="z_appointment.appointment",
        string="Visit",
        domain="[('state','in', ('3', '4', '5', '6', '7', '8'))]",
        required=True,
    )
    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        related="visit_id.customer_id",
    )
    icd_ids = fields.Many2many('z_medical_record.icd_10', string='ICD Codes')

    code = fields.Char(string="Medical result code")
    examination_type = fields.Char(string="Examination type")
    pdf_title = fields.Char(string="Pdf title", compute="_compute_pdf_title")
    examination_date = fields.Date("Examination date", tracking=True)  # Ngày khám
    reexamination_date = fields.Date(
        "Reexamination date", tracking=True
    )  # Ngày tái khám
    reason = fields.Text("Reason")  # Lý do khám
    result = fields.Text("Result")  # Kết quả khám
    solution = fields.Text("Solution")  # Phương án xử lý
    note = fields.Text("Note")  # Lưu ý
    is_editable = fields.Boolean(string="Is Editable", compute="_compute_is_editable")

    @api.depends("examination_date")
    def _compute_is_editable(self):
        for record in self:
            if record.examination_date:
                # Appointment date
                appointment_date = fields.Date.from_string(record.examination_date)
                # End of the day following the appointment date
                end_edit_datetime = datetime.combine(
                    appointment_date + timedelta(days=1), datetime.min.time()
                )
                # Current time
                current_datetime = fields.Datetime.now()
                # Check if current time is within the allowed editing window
                record.is_editable = current_datetime <= end_edit_datetime
            else:
                record.is_editable = False

    _sql_constraints = [
        (
            "unique_visit_id",
            "unique(visit_id)",
            "Visit must be unique",
        )
    ]

    @api.depends("customer_id", "examination_type", "examination_date")
    def _compute_pdf_title(self):
        for record in self:
            name = unidecode(record.customer_id.name).replace(" ", "")
            record.pdf_title = f"{record.examination_type}_{record.customer_id.code}_{name}_{record.examination_date}"
