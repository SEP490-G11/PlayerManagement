from odoo.addons.component.core import Component
from odoo.tools.safe_eval import safe_eval
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo import fields, exceptions, _
from odoo.addons.base_rest.components.service import to_bool, to_int
from pytz import timezone, UTC
from odoo.addons.base_rest import restapi
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime, date, time
import logging
import json
from odoo import SUPERUSER_ID
from pytz import timezone, utc
import re
from odoo import http
from odoo.addons.z_web.helpers.response import ResponseUtils
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_appointment.helpers.utils import ZAppointmentUtils
from odoo.addons.z_hr.helpers.time_slot_utils import ZTimeSlotUtils
from odoo.addons.z_web.helpers.constants import (
    STANDARD_DATE_FORMAT,
    STANDARD_TIME_FORMAT,
    ErrorCode,
)

from odoo.addons.z_appointment.helpers.constants import (
    DEFAULT_APPOINTMENT_SORT,
    APPOINTMENT_START_TIME,
    APPOINTMENT_SORT_DICT,
    APPOINTMENT_STATE_VALUES,
    VISIT_STATE_LIST,
    BOOKING_TYPE_VALUES,
    BookingType,
    HEADER_STYLE,
    CONTENT_STYLE,
    DATE_FIELDS,
    AppointmentType
)

log = logging.getLogger(__name__)

class iCareService(Component):
    _inherit = "base.rest.service"
    _name = "icare.service.info"
    _usage = "v1"
    _collection = "all.rest.api.services"
    _description = """iCare Services"""
    _log_calls_in_db = True

    @restapi.method([(["/create-user"], "POST")], input_param=Datamodel("token.datamodel"))
    def authToken(self, params):
        user = params.username
        password = params.password

        user = (
            self.env["res.users"]
            .sudo()
            .create({"name": user, "login": user, "password": password})
        )

        return {
            "message": "Success",
            "data": {
                "user": user.name
            }
        }

    @restapi.method(
        [(["/get-list-timeslot"], "GET")],
        input_param=Datamodel("get.listTimeSlot"),
        output_param=restapi.CerberusValidator("_get_list_timeslot_schema"),
    )
    def getListTimeSlots(self, param_list_time_slot):
        expect_time = param_list_time_slot.expected_date
        place_id = param_list_time_slot.place_id
        overbook = 0

        try:
            if expect_time:
                start_at = expect_time + " 00:00:00"
                end_at = expect_time + " 23:59:59"
                search_domain = [
                    ("enable", "=", True),
                    ("start_time", ">=", start_at),
                    ("start_time", "<=", end_at),
                    ("booked", "=", bool(overbook)),
                    ("employee_id.is_doctor", "=", True)
                ]
            else:
                search_domain = [
                    ("enable", "=", True),
                    ("start_time", ">=", ZUtils.now()),
                ]
            if place_id:
                http.request.env["z_place.place"].get_place_by_id(place_id)
                search_domain.append(("place_id", "=", int(place_id)))

            results = (
                http.request.env["z_hr.time_slot"].sudo()
                .search(search_domain, order="start_time asc")
            )
            doctors = results.mapped("employee_id")
            doctors = [
                {
                    "id": item.id,
                    "name": item.name
                }
                for item in doctors
            ]

            timeslots = [
                {
                    "id": item.id,
                    "doctor_id": item.employee_id.id,
                    "doctor_name": next(
                        (doctor["name"] for doctor in doctors if doctor["id"] == item.employee_id.id),
                        'N/A'
                    ),
                    "booking_date": ZUtils.format_datetime(item.start_time),
                    "booking_time": ZUtils.format_datetime(
                        item.start_time, STANDARD_TIME_FORMAT
                    ),
                    "is_overbook": item.booked,
                    "place_id": item.place_id.id if item.place_id else None,
                }
                for item in results
            ]

            return {
                "code": 200,
                "message": "Success",
                "doctors": doctors,
                "timeslots": timeslots
            }
        except Exception as e:
            log.exception("An error occurred in getListTimeSlots: %s", str(e))
            return {
                "code": 400,
                "message": str(e),
                "doctors": [],
                "timeslots": []
            }

    def _get_list_timeslot_schema(self):
        return {
            "code": {"type": "integer", "required": True},
            "message": {"type": "string", "required": True},
            "doctors": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "id": {"type": "integer", "required": True},
                        "name": {"type": "string"}
                    }
                },
                "required": True
            },
            "timeslots": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "id": {"type": "integer"},
                        "booking_date": {"type": "string"},
                        "doctor_name": {"type": "string"},
                        "booking_time": {"type": "string"},
                        "is_overbook": {"type": "boolean"},
                        "doctor_id": {"type": "integer"},
                        "place_id": {"type": "integer"}
                    }
                },
                "required": True
            }
        }

    @restapi.method(
        [(["/book-appointment"], "POST")],
        input_param=Datamodel("book.appointment"),
        output_param=restapi.CerberusValidator("_book_appointment_schema"),
    )
    def bookAppointment(self, params):
        try:
            appointment_instance = http.request.env["z_appointment.appointment"]
            time_slot_instance = http.request.env["z_hr.time_slot"]
            time_slot_id = int(params.timeslot_id)
            customer_name = str(params.customer_name)
            customer_gender = str(params.customer_gender)
            customer_phonenumber = str(params.customer_phonenumber)
            note = params.note if params.note else ""
            user_id = params.user_id
            # lay du lieu time slot
            time_slot = http.request.env["z_hr.time_slot"].sudo().search(
                [("id", "=", time_slot_id), ("enable", "=", True)], limit=1)
            if time_slot is None:
                return {"code": 400, "message": "Timeslot not found"}

            # validate xem timeslot co phu hop khong
            appointment = None
            overbook = False
            booking_type = BookingType.BY_DATE
            doctor_id = time_slot.employee_id.id
            print("doctor_id", doctor_id)
            technician_id = 0
            ZAppointmentUtils.check_valid_appointment(time_slot, appointment)
            ZAppointmentUtils.check_overbook(overbook, time_slot, appointment)
            ZAppointmentUtils.validate_time_slot_by_booking_type(
                appointment_instance,
                booking_type,
                overbook,
                doctor_id,
                technician_id,
                time_slot,
                appointment,
            )

            # lay them thong tin khach hang neu co
            customer_info = http.request.env["res.partner"].sudo().search(
                [("name", "=", customer_name), ("mobile", "=", customer_phonenumber)]
                , limit=1
            )
            customer_group = http.request.env["z_partner.group"].sudo().search(
                [("name", "=", "vivision")]
                , limit=1
            )

            # // TODO - query group theo name la vivision
            customer_id = 0
            if not customer_gender:
                customer_gender = 'n/a'
            
            
            if customer_info:
                customer_id = customer_info.id
            else:
                # TODO - can thao luan xem group_id xet the nao
                customer_info = {
                  "group_id": customer_group.id,
                  "name": customer_name,
                  "date": None,
                  "gender": customer_gender,
                  "mobile": customer_phonenumber,
                  "job": "",
                  "is_customer": True
                }
                customer = http.request.env["res.partner"].sudo().create(customer_info)
                customer_id = customer.id

            payload = {
                "booking_type": booking_type,
                "customer_id": customer_id,
                "time_slot_id": time_slot.id,
                "doctor_id": doctor_id,
                "technician_id": technician_id,
                "type": AppointmentType.NEW_EXAMINATION,
                "overbook": overbook,
                "examination_reason": '',
                "note": note,
                "write_uid": 1,
                "pancake_user_id": user_id
            }
            appointment = appointment_instance.sudo().create(payload)
            employee_ids = [appointment.doctor_id.id]
            time_slot_instance.sudo().search(
                [("employee_id", "in", employee_ids), ("start_time", "=", appointment.time_slot_id.start_time)]
            ).write({"booked": True})
            return {
                "code": 200,
                "message": "Success",
                "data": {
                    "appointment_id": appointment.id,
                    "place_name": time_slot.place_id.name,
                    "booking_date": ZUtils.format_datetime(time_slot.start_time),
                    "booking_time": ZUtils.format_datetime(
                        time_slot.start_time, STANDARD_TIME_FORMAT
                    ),
                    "doctor_name": time_slot.employee_id.name,
                    "optom_name": "",
                    "overbook": False,
                    "note": note,
                }
            }
        except Exception as e:
            log.exception("An error occurred in bookAppointment: %s", str(e))
            return {
                "code": 400,
                "message": str(e)
            }
        except Exception as e:
            log.exception("An error occurred in bookAppointment: %s", str(e))
            return {
                "code": 400,
                "message": str(e),
                "doctors": [],
                "timeslots": []
            }

    def _book_appointment_schema(self):
        return {
            "code": {"type": "integer", "required": True},
            "message": {"type": "string", "required": True},
            "data": {
                "type": "dict",
                "schema": {
                    "appointment_id": {"type": "integer"},
                    "place_name": {"type": "string"},
                    "booking_date": {"type": "string"},
                    "booking_time": {"type": "string"},
                    "doctor_name": {"type": "string"},
                    "optom_name": {"type": "string"},
                    "overbook": {"type": "boolean"},
                    "note": {"type": "string"},
                    "user_id": {"type":"string"},
                },
                "required": False
            }
        }
