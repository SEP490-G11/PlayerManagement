# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.addons.z_web.helpers.response import ResponseUtils
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_web.helpers.constants import ErrorCode


class ZEmployeeController(http.Controller):
    @http.route(
        "/z_hr/employee/get_list_doctor_and_technician", auth="user", methods=["GET"]
    )
    def get_list_doctor_and_technician(self, **kw):
        try:
            expect_time = kw.get("expect_time", None)
            overbook = int(kw.get("overbook", 0))
            is_doctor = int(kw.get("is_doctor", 0))
            place_id = kw.get("place_id", None)
            if expect_time:
                exist_ids = ZUtils.parse_to_list_id(kw, "existIds")
                search_domain = [
                    "&",
                    ("start_time", "=", expect_time),
                    ("enable", "=", True),
                    "|",
                    "|",
                    ("employee_id", "in", exist_ids),
                    "&",
                    ("booked", "=", bool(overbook)),
                    ("employee_id.is_doctor", "=", is_doctor),
                    "&",
                    ("booked", "=", False),
                    ("employee_id.is_doctor", "!=", is_doctor),
                ]
            else:
                search_domain = [
                    ("enable", "=", True),
                    ("start_time", ">=", ZUtils.now()),
                ]
            if place_id:
                http.request.env["z_place.place"].get_place_by_id(place_id)
                search_domain.append(("place_id", "=", int(place_id)))
            employees = (
                http.request.env["z_hr.time_slot"]
                .search(search_domain)
                .mapped("employee_id")
            )
            employees = [
                {
                    "id": item.id,
                    "name": item.name,
                    "is_doctor": item.job_id.is_doctor,
                }
                for item in employees
            ]
            return ResponseUtils.res(employees)
        except UserError as code:
            return ResponseUtils.err(code=code)
        except Exception:
            return ResponseUtils.err(code=ErrorCode.INTERNAL_SERVER_ERROR)
