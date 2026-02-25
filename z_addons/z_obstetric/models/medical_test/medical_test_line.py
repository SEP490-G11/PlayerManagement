# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import boto3
from odoo.exceptions import ValidationError


class ZMedicalTestLine(models.Model):
    _name = "z_obstetric.medical_test_line"
    _description = "Medical test"

    service_id = fields.Many2one(
        "product.product",
        string="Medical test name",
        domain="[('detailed_type','=', 'service')]",
        required=True,
    )
    medical_test_id = fields.Many2one("z_obstetric.medical_test", ondelete="cascade")

    visit_id = fields.Many2one("z_appointment.appointment", ondelete="cascade")
    result_image_url = fields.Text("Result image url path")
    file = fields.Binary("File", restore=False)
    has_result = fields.Boolean("Has result", compute="_compute_has_result")

    def action_open_form(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "amazon_s3_connector.amazon_upload_file_action"
        )
        action["context"] = {"default_record_id": self.id}
        return action

    def action_preview_result(self):
        if self.has_result:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "z_web.preview_iframe_view_action"
            )
            url = f"/get-image?key={self.result_image_url}"
            action["context"] = {"default_url": url}
            return action

    @api.depends("result_image_url")
    def _compute_has_result(self):
        for rec in self:
            rec.has_result = bool(rec.result_image_url)

    # def action_print(self):
    # action = self.env["ir.actions.report"]._for_xml_id(
    #     "z_obstetric.action_report_obstetric_test"
    # )
    # return action

    def action_print(self):
        pdf_url = "/get-image?key=" + self.result_image_url
        return {
            "type": "ir.actions.act_url",
            "url": "/print-pdf?url=" + pdf_url,
            "target": "new",
        }

    def action_unlink(self):
        self.ensure_one()
        self.unlink()
