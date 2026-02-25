import json
import logging
import requests
import urllib.parse
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_zns.helpers.constants import BASE_URL
from odoo.addons.z_web.helpers.constants import READABLE_DATE_FORMAT

_logger = logging.getLogger(__name__)


class ZNSUltils:
    @staticmethod
    def zns_352020(instance, data_zns):
        phone = data_zns["customer_phone"].replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "352020", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}
            payload = {
                "phone": phone,
                "template_id": "352020",
                "template_data": {
                    "customer_name": data_zns["customer_name"],
                    "invoice_id": data_zns["invoice_id"],
                    "schedule_date": data_zns["schedule_date"],
                    "end_date": data_zns["end_date"],
                    "customer": data_zns["customer_name"],
                },
                "tracking_id": data_zns["appointment_id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_352020(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "352020", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_365664(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "365664", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}
            schedule_time = data_zns.booking_time
            schedule_time += ":00 "
            schedule_time += ZUtils.format_datetime(
                data_zns.booking_date, READABLE_DATE_FORMAT
            )

            payload = {
                "phone": data_zns.customer_id.mobile.replace(" ", "").replace("+", ""),
                "template_id": "365664",
                "template_data": {
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                    "address": data_zns.place_id.name,
                    "schedule_time": schedule_time,
                },
                "tracking_id": data_zns["id"],
            }
            print("payload", payload)
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_365707(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "365664", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_366061(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "366061", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}
            schedule_time = data_zns.booking_time
            schedule_time += ":00 "
            schedule_time += ZUtils.format_datetime(
                data_zns.booking_date, READABLE_DATE_FORMAT
            )
            payload = {
                "phone": data_zns.customer_id.mobile.replace(" ", "").replace("+", ""),
                # "phone": '84984203569',
                "template_id": "366061",
                "template_data": {
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                    "address": data_zns.place_id.name,
                    "schedule_time": schedule_time,
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_365707(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "366061", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_366060(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "366060", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}
            schedule_time = data_zns.booking_time
            schedule_time += ":00 "
            schedule_time += ZUtils.format_datetime(
                data_zns.booking_date, READABLE_DATE_FORMAT
            )
            payload = {
                "phone": data_zns.customer_id.mobile.replace(" ", "").replace("+", ""),
                # "phone": '84984203569',
                "template_id": "366060",
                "template_data": {
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                    "address": data_zns.place_id.name,
                    "schedule_time": schedule_time,
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_365707(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "366060", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_365707(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        status = True
        message = ""
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            print(phone)
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "365707", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            schedule_time = data_zns.booking_time
            schedule_time += ":00 "
            schedule_time += ZUtils.format_datetime(
                data_zns.booking_date, READABLE_DATE_FORMAT
            )

            payload = {
                "phone": data_zns.customer_id.mobile.replace(" ", "").replace("+", ""),
                # "phone": '84984203569',
                "template_id": "365707",
                "template_data": {
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                    "address": data_zns.place_id.name,
                    "schedule_time": schedule_time,
                },
                "tracking_id": data_zns["id"],
            }

            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]
            print("response", resultZns)
            print("errorZns", errorZns)
            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_365707(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "365707", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_365897(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "365897", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}
            schedule_time = data_zns.booking_time
            schedule_time += ":00 "
            schedule_time += ZUtils.format_datetime(
                data_zns.booking_date, READABLE_DATE_FORMAT
            )
            payload = {
                "phone": phone,
                "template_id": "365897",
                "template_data": {
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                    "address": data_zns.place_id.name,
                    "schedule_time": schedule_time,
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_365897(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "365897", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_365888(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "365888", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            payload = {
                "phone": phone,
                "template_id": "365888",
                "template_data": {
                    "address": data_zns.visit_id.place_id.name,
                    "p_date": ZUtils.format_datetime(
                        data_zns.order_date, READABLE_DATE_FORMAT
                    ),
                    "delivery_method": dict(
                        data_zns._fields["delivery_method"].selection
                    ).get(data_zns.delivery_method),
                    "recipient": data_zns.recipient_name,
                    "phone_number": data_zns.customer_id.mobile.replace(
                        " ", ""
                    ).replace("+", ""),
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_365888(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "365888", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_365736(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "365736", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            payload = {
                "phone": data_zns.customer_id.mobile.replace(" ", "").replace("+", ""),
                "template_id": "365736",
                "template_data": {
                    "address": data_zns.visit_id.place_id.name,
                    "estimate_date": ZUtils.format_datetime(
                        data_zns.order_date, READABLE_DATE_FORMAT
                    ),
                    "delivery_method": dict(
                        data_zns._fields["delivery_method"].selection
                    ).get(data_zns.delivery_method),
                    "recipient": data_zns.recipient_name,
                    "phone_number": data_zns.customer_id.mobile.replace(
                        " ", ""
                    ).replace("+", ""),
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_365736(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "365736", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_365893(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "365893", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            payload = {
                "phone": phone,
                "template_id": "365893",
                "template_data": {
                    "date": ZUtils.format_datetime(
                        data_zns.tracking_date, READABLE_DATE_FORMAT
                    ),
                    "combo_name": data_zns.combo_id.name,
                    "phone_number": data_zns.customer_id.mobile.replace(
                        " ", ""
                    ).replace("+", ""),
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_365893(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "365893", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_365894(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "365893", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            payload = {
                "phone": phone,
                "template_id": "365894",
                "template_data": {
                    "date": ZUtils.format_datetime(
                        data_zns.tracking_date, READABLE_DATE_FORMAT
                    ),
                    "combo_name": data_zns.combo_id.name,
                    "phone_number": data_zns.customer_id.mobile.replace(
                        " ", ""
                    ).replace("+", ""),
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_365894(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "365894", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_397617(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "397617", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            payload = {
                "phone": phone,
                "template_id": "397617",
                "template_data": {
                    "customer_name": data_zns.customer_id.name,
                    "order_id": data_zns.customer_id.mobile.replace(" ", "").replace(
                        "+", ""
                    ),
                    "order_code": "khám mắt",
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_397617(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = "Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "397617", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_421915(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "421915", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            payload = {
                "phone": phone,
                "template_id": "421915",
                "template_data": {
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.mobile.replace(" ", "").replace(
                        "+", ""
                    ),
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_421915(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "421915", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_422789(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "422789", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            payload = {
                "phone": phone,
                "template_id": "422789",
                "template_data": {
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.mobile.replace(" ", "").replace(
                        "+", ""
                    ),
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_422789(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "422789", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_422787(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "422787", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            payload = {
                "phone": phone,
                "template_id": "422787",
                "template_data": {
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.mobile.replace(" ", "").replace(
                        "+", ""
                    ),
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_422787(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "422787", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_421920(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "421920", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            payload = {
                "phone": phone,
                "template_id": "421920",
                "template_data": {
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.mobile.replace(" ", "").replace(
                        "+", ""
                    ),
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_421920(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "421920", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_391172(instance, data_zns):
        phone = ZNSUltils.convert_phone_number(
            data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        )
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "391172", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}

            payload = {
                "phone": phone,
                "template_id": "391172",
                "template_data": {
                    "order_date": data_zns.booking_date.strftime("%d/%m/%Y"),
                    "customer_name": data_zns.customer_id.name,
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -1241:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_391172(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "391172", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def reget_access_token(instance):
        try:
            appId = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_app_id")
            )
            secretKey = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_secret_key")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )

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
            response = requests.post(
                "https://oauth.zaloapp.com/v4/oa/access_token",
                headers=headers,
                data=encoded_payload,
            )
            resultZns = response.json()
            if resultZns["access_token"]:
                instance.env["ir.config_parameter"].sudo().set_param(
                    "z_zns.z_system_zns_access_token", resultZns["access_token"]
                )
                instance.env["ir.config_parameter"].sudo().set_param(
                    "z_zns.z_system_zns_refresh_token", resultZns["refresh_token"]
                )
                return True
            else:
                _logger.error(
                    f"Failed to reget access token. Status code: {resultZns['error_name']}, Response: {resultZns['error_description']}",
                    resultZns,
                )
                return False
        except Exception as e:
            _logger.error("Failed to reget access token: %s", e)
            return False

    @staticmethod
    def add_zns_history(instance, phone, template_id, data, status, message=None):
        history = instance.env["zns.history"].create(
            {
                "phone": phone,
                "type": template_id,
                "status": status,
                "message": message,
                "data": json.dumps({"original_data": str(data)}),
            }
        )
        return history

    @staticmethod
    def convert_phone_number(phone):
        if phone.startswith("0") and phone[1:].isdigit():
            return "84" + phone[1:]
        return phone

    @staticmethod
    def zns_429776(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "429776", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}
            schedule_time = data_zns.booking_time
            schedule_time += ":00 "
            schedule_time += ZUtils.format_datetime(
                data_zns.booking_date, READABLE_DATE_FORMAT
            )
            payload = {
                "phone": phone,
                "template_id": "429776",
                "template_data": {
                    "address": data_zns.place_id.address,
                    "schedule_time": schedule_time,
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.mobile.replace(" ", "").replace(
                        "+", ""
                    ),
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_429776(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "429776", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_429779(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "429779", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}
            schedule_time = data_zns.booking_time
            schedule_time += ":00 "
            schedule_time += ZUtils.format_datetime(
                data_zns.booking_date, READABLE_DATE_FORMAT
            )
            payload = {
                "phone": phone,
                "template_id": "429779",
                "template_data": {
                    "address": data_zns.place_id.address,
                    "schedule_time": schedule_time,
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.mobile.replace(" ", "").replace(
                        "+", ""
                    ),
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_429779(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "429779", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_399184(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "399184", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}
            schedule_time = data_zns.booking_time
            schedule_time += ":00 "
            schedule_time += ZUtils.format_datetime(
                data_zns.booking_date, READABLE_DATE_FORMAT
            )
            payload = {
                "phone": phone,
                "template_id": "399184",
                "template_data": {
                    "address": data_zns.place_id.address,
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                    "schedule_time": schedule_time,
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_399184(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "399184", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)

    @staticmethod
    def zns_399185(instance, data_zns):
        phone = data_zns.customer_id.mobile.replace(" ", "").replace("+", "")
        try:
            accessToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_access_token")
            )
            refreshToken = (
                instance.env["ir.config_parameter"]
                .sudo()
                .get_param("z_zns.z_system_zns_refresh_token")
            )
            status = True
            message = ""
            if not accessToken or not refreshToken:
                status = False
                message = "Access Token or Refresh Token is missing"
                ZNSUltils.add_zns_history(
                    instance, phone, "399185", data_zns, status, message
                )
                return False

            headers = {"Content-Type": "application/json", "access_token": accessToken}
            schedule_time = data_zns.booking_time
            schedule_time += ":00 "
            schedule_time += ZUtils.format_datetime(
                data_zns.booking_date, READABLE_DATE_FORMAT
            )
            payload = {
                "phone": phone,
                "template_id": "399185",
                "template_data": {
                    "address": data_zns.place_id.address,
                    "customer_name": data_zns.customer_id.name,
                    "customer_id": data_zns.customer_id.code,
                    "schedule_time": schedule_time,
                },
                "tracking_id": data_zns["id"],
            }
            response = requests.post(
                BASE_URL, headers=headers, data=json.dumps(payload)
            )
            resultZns = response.json()
            errorZns = resultZns["error"]

            if errorZns == 0:
                message = "ZNS message sent successfully."
            elif errorZns == -124:
                regetAccessToken = ZNSUltils.reget_access_token(instance)
                if regetAccessToken:
                    ZNSUltils.zns_399185(instance, data_zns)
                else:
                    message = "Access token or refresh token not reget."
                    status = False
            else:
                message = f"Failed to send ZNS message. Status code: {resultZns['error']}, Response: {resultZns['message']}"
                status = False
        except Exception as e:
            _logger.error("Failed to send message zns: %s", e)
            message = "Failed to send message zns: {}".format(e)
            status = False
        zns_history = ZNSUltils.add_zns_history(
            instance, phone, "399185", resultZns, status, message
        )
        return (status, message, zns_history.msg_id)
