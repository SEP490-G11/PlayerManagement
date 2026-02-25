# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.addons.z_hr.helpers.time_slot_utils import ZTimeSlotUtils
from odoo.addons.z_web.helpers.response import ResponseUtils
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_web.helpers.validation import ZValidation
from odoo.addons.z_web.helpers.constants import (
    STANDARD_DATE_FORMAT,
    STANDARD_TIME_FORMAT,
    ErrorCode,
)


class ZTimeSlotController(http.Controller):
    @http.route("/z_hr/timeslots", auth="user", methods=["GET"])
    def get_time_slots(self, **kw):
        try:
            ZValidation.validate_required_field(kw, ["expect_date", "place_id"])
            employee_id = ZUtils.get(kw, "employee_id", int)
            place_id = ZUtils.get(kw, "place_id", int)

            http.request.env["z_place.place"].get_place_by_id(place_id)
            employee = None
            if employee_id:
                employee = http.request.env["hr.employee"]._get_employee_by_id(
                    employee_id
                )

            # Filter all timeslots by expect time and employee id
            records = ZTimeSlotUtils.filter_time_slots(http.request, kw)

            # Case booking by technician >> filter out all timeslots which having start time with no doctor
            if employee and employee.bookable and not employee.is_doctor:
                records = ZTimeSlotUtils.filter_valid_time_slots(http.request, records)

            data = [
                {
                    "id": item.id,
                    "employee_id": item.employee_id.id,
                    "is_doctor": item.employee_id.is_doctor,
                    "examination_date": ZUtils.format_datetime(item.start_time),
                    "start_time": ZUtils.format_datetime(
                        item.start_time, STANDARD_TIME_FORMAT
                    ),
                    "enable": item.enable,
                    "booked": item.booked,
                    "place_id": item.place_id.id if item.place_id else None,
                }
                for item in records
            ]
            return ResponseUtils.res(data=data)
        except ValidationError as e:
            return ResponseUtils.err(msg=str(e))
        except UserError as code:
            return ResponseUtils.err(code=code)
        except Exception:
            return ResponseUtils.err(code=ErrorCode.INTERNAL_SERVER_ERROR)

    @http.route(
        "/z_hr/timeslots/get_slots_with_doctor_working", auth="user", methods=["GET"]
    )
    def get_slots_with_doctor_working(self, **kw):
        start_at = kw.get("startDate", "")
        end_at = kw.get("endDate", "")
        place_id = int(kw.get("place_id"))
        try:
            if place_id:
                http.request.env["z_place.place"].get_place_by_id(place_id)
            start_at = ZUtils.str_to_datetime(start_at, STANDARD_DATE_FORMAT)
            end_at = ZUtils.str_to_datetime(end_at, STANDARD_DATE_FORMAT) + timedelta(
                days=1
            )
            instance = http.request.env["z_hr.time_slot"]
            records = sorted(
                set(
                    ZTimeSlotUtils.filter_slots_with_doctors_working(
                        instance, start_at, end_at, place_id
                    ).mapped("start_time")
                )
            )
            data = ZTimeSlotUtils.get_slots_results(records)
            return ResponseUtils.res(data=data)
        except Exception:
            return ResponseUtils.err(ErrorCode.INTERNAL_SERVER_ERROR)
