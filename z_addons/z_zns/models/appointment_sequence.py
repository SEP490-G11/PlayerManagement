# -*- coding: utf-8 -*-
import json
import logging
import requests
import urllib.parse
from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_web.helpers.constants import READABLE_DATE_FORMAT
from odoo.addons.z_appointment.helpers.constants import AppointmentState


_logger = logging.getLogger(__name__)


class ZAppointmentSequence(models.Model):
    _name = "z.appointment.sequence"
    _description = "Appointment Sequence"

    name = fields.Char(string="Appointment Sequence")

    @api.model
    def send_zns_after_finish_appointment(self):
        now = fields.Datetime.now()
        comparision_time = now - timedelta(hours=2)
        print(comparision_time)
        appointments = self.env['z_appointment.appointment'].search([
            ('state', '=', AppointmentState.FINISHED),
            ('finish_time', '<=', comparision_time),
            ('has_sent_zns_finish_time', '=', False),
        ])

        for appointment in appointments:
            appointment_info = {
                'customer_name': appointment.customer_id.name,
                'invoice_id': appointment.examination_code,
                'schedule_date': ZUtils.format_datetime(appointment.booking_date, READABLE_DATE_FORMAT),
                'end_date': ZUtils.format_datetime(appointment.finish_time, READABLE_DATE_FORMAT),
                'customer': appointment.customer_id.name,
                 'customer_phone': appointment.customer_id.mobile,
                #'customer_phone': '84984203569',
                'appointment_id': appointment.id,
            }
            success, message, zns_message_object = self.send_zns_for_finish_time(
                appointment_info
            )
            try:
                zns_message_data = json.dumps(zns_message_object)
            except (TypeError, ValueError) as e:
                zns_message_data = json.dumps(
                    {"error": str(e), "original_data": str(zns_message_object)}
                )

            appointment.write({"has_sent_zns_finish_time": True})
            self.env["zns.history"].create(
                {
                    "customer_name": appointment_info["customer_name"],
                    "data_id": appointment_info["appointment_id"],
                    "phone": appointment_info["customer_phone"],
                    "type": "appointment_finish_time",
                    "status": success,
                    "data": zns_message_data,
                }
            )
            if not success:
                print(f"Failed to send ZNS for appointment {appointment.id}: {message}")

    def send_zns_for_finish_time(self, appointment_info):
        # query lai access token, refresh token
        try:
            accessToken = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            if not accessToken or not refreshToken:
                return (
                    False,
                    "Access token or refresh token not found.",
                    {message: "Access token or refresh token not found."},
                )
            url = "https://business.openapi.zalo.me/message/template"
            headers = {"Content-Type": "application/json", "access_token": accessToken}
            payload = {
                "phone": appointment_info['customer_phone'].replace(" ", "").replace("+", ""),
                "template_id": "352020",
                "template_data": {
                    "customer_name": appointment_info['customer_name'],
                    "invoice_id": appointment_info['invoice_id'],
                    "schedule_date": appointment_info['schedule_date'],
                    "end_date": appointment_info['end_date'],
                    "customer": appointment_info['customer_name']
                 },
                "tracking_id": appointment_info['appointment_id']
            }
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            resultZns = response.json()
            errorZns = resultZns["error"]
            if errorZns == 0:
                return True, "ZNS message sent successfully.", resultZns
            elif errorZns == -124:
                # update lai access token
                return self.reget_access_token(appointment_info)
            else:
                return (
                    False,
                    f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}",
                    resultZns,
                )
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            return False, f"Failed to send ZNS message: {str(e)}", e

    def reget_access_token(self, appointment_info):
        try:
            appId = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_app_id")
            )
            secretKey = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_secret_key")
            )
            refreshToken = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )

            url = "https://oauth.zaloapp.com/v4/oa/access_token"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "secret_key": secretKey,
            }

            payload = {
                "refresh_token": refreshToken,
                "app_id": appId,
                "grant_type": "refresh_token",
            }

            encoded_payload = urllib.parse.urlencode(payload)
            response = requests.post(url, headers=headers, data=encoded_payload)
            resultZns = response.json()
            if resultZns["access_token"]:
                self.env["ir.config_parameter"].sudo().set_param(
                    "z_zns.z_system_zns_access_token", resultZns["access_token"]
                )
                self.env["ir.config_parameter"].sudo().set_param(
                    "z_zns.z_system_zns_refresh_token", resultZns["refresh_token"]
                )
                return self.send_zns_for_finish_time(appointment_info)
            else:
                return (
                    False,
                    f"Failed to reget access token. Status code: {resultZns['error_name']}, Response: {resultZns['error_description']}",
                    resultZns,
                )
        except Exception as e:
            _logger.error("Failed to reget access token: %s", e)
            return False, f"Failed to reget token ZNS message: {str(e)}", e
