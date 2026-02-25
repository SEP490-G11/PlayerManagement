# -*- coding: utf-8 -*-

from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.addons.z_appointment.helpers.utils import ZAppointmentUtils
from odoo.addons.z_appointment.helpers.constants import (
    APPOINTMENT_TYPE_DICT,
    APPOINTMENT_STATE_DICT,
)
from odoo.addons.z_web.helpers.constants import ErrorCode
from odoo.addons.z_web.helpers.request import ZRequest
from odoo.addons.z_web.helpers.response import ResponseUtils
from odoo.addons.z_web.helpers.utils import ZUtils


class ZAppointmentController(http.Controller):
    @http.route("/z_appointment/appointment", auth="user", methods=["GET"])
    def list(self, **kw):
        try:
            is_not_paging = ZUtils.get(kw, "is_not_paging", int)
            env = http.request.env["z_appointment.appointment"]
            search_domain, order = ZAppointmentUtils.filter_appointments_or_visits(kw)
            if is_not_paging:
                records = env.search(search_domain)
                items = ZAppointmentUtils.format_results(records)
                return ResponseUtils.res(items)
            else:
                total_count = env.search_count(search_domain)
                pagination_info = ResponseUtils.get_paginated_info(total_count, kw)
                offset = pagination_info["offset"]
                records = env.search(
                    search_domain,
                    order=order,
                    offset=offset,
                    limit=kw.get("page_size", 20),
                )
                items = ZAppointmentUtils.format_results(records, offset)
                return ResponseUtils.res(dict(items=items, **pagination_info))
        except Exception as e:
            return ResponseUtils.err(e)

    @http.route("/z_appointment/appointment", auth="user", methods=["POST"])
    def create_appointment(self, **kw):
        try:
            payload = ZRequest.parse_to_json(kw)
            appointment = ZAppointmentUtils.create_or_update(http.request, payload)
            return ResponseUtils.res(
                ZAppointmentUtils.format_detail(appointment), "Đặt lịch thành công"
            )
        except ValidationError as e:
            return ResponseUtils.err(msg=str(e))
        except UserError as code:
            return ResponseUtils.err(code=code)
        except Exception:
            return ResponseUtils.err(code=ErrorCode.INTERNAL_SERVER_ERROR)

    @http.route("/z_appointment/appointment", auth="user", methods=["PUT"])
    def update_appointment(self, **kw):
        try:
            payload = ZRequest.parse_to_json(kw)
            appointment = ZAppointmentUtils.create_or_update(
                http.request, payload, True
            )
            return ResponseUtils.res(
                ZAppointmentUtils.format_detail(appointment),
                "Đổi lịch thành công",
            )
        except ValidationError as e:
            return ResponseUtils.err(msg=str(e))
        except UserError as code:
            return ResponseUtils.err(code=code)
        except Exception:
            return ResponseUtils.err(code=ErrorCode.INTERNAL_SERVER_ERROR)

    @http.route(
        "/z_appointment/appointment/update_state/<int:id>", auth="user", methods=["PUT"]
    )
    def update_appointment_state(self, **kw):
        try:
            payload = ZRequest.parse_to_json(kw)
            state = payload.get("state")
            is_visit = payload.get("is_visit")
            ZAppointmentUtils.validate_appointment_state(state, is_visit)
            appointment = http.request.env[
                "z_appointment.appointment"
            ]._get_appointment_by_id(payload.get("id"))
            appointment.write({"state": state })
            if not appointment.examination_code:
                appointment.examination_code = ZAppointmentUtils.generate_examination_code(
                    http.request, appointment.booking_date
                )
                appointment.has_took_examination = True
            label = "lượt khám" if is_visit else "lịch hẹn"
            return ResponseUtils.res(
                ZAppointmentUtils.format_detail(appointment),
                f"Đổi trạng thái {label} thành công",
            )
        except ValidationError as e:
            return ResponseUtils.err(msg=str(e))
        except UserError as code:
            return ResponseUtils.err(code=code)
        except Exception:
            return ResponseUtils.err(code=ErrorCode.INTERNAL_SERVER_ERROR)

    @http.route(
        "/z_appointment/appointment/update_printing_type/<int:id>", auth="user", methods=["PUT"]
    )
    def update_appointment_printing_type(self, **kw):
        try:
            payload = ZRequest.parse_to_json(kw)
            printingType = payload.get("type")
            appointment = http.request.env[
                "z_appointment.appointment"
            ]._get_appointment_by_id(payload.get("id"))
            appointment.printing_type = printingType
            return ResponseUtils.res(
                ZAppointmentUtils.format_detail(appointment),
                f"Đổi phiếu in thành công",
            )
        except ValidationError as e:
            return ResponseUtils.err(msg=str(e))
        except UserError as code:
            return ResponseUtils.err(code=code)
        except Exception:
            return ResponseUtils.err(code=ErrorCode.INTERNAL_SERVER_ERROR)



    @http.route("/z_appointment/appointment/<int:id>", auth="user", methods=["DELETE"])
    def delete_appointment(self, **kw):
        """
        :param: id: int, //required
        :return: {}
        """
        try:
            appointment = http.request.env[
                "z_appointment.appointment"
            ]._get_appointment_by_id(kw.get("id"))
            ZAppointmentUtils.release_slots(
                http.request.env["z_hr.time_slot"], appointment
            )
            appointment.unlink()
            return ResponseUtils.res({}, "Đã xóa lịch hẹn thành công")
        except UserError as code:
            return ResponseUtils.err(code=code)
        except Exception:
            return ResponseUtils.err(code=ErrorCode.INTERNAL_SERVER_ERROR)

    @http.route("/z_appointment/appointment/export_excel", auth="user", methods=["GET"])
    def export_appointment(self, **kw):
        try:
            queryset = http.request.env["z_appointment.appointment"].search([])
            filename = "Danh-sach-lich-hen"
            headings = [
                "STT",
                "Nhóm khách hàng",
                "Ngày",
                "Thời gian",
                "Tên khách hàng",
                "Số điện thoại",
                "Loại lịch",
                "Kỹ thuật viên",
                "Bác sĩ",
                "Trạng thái",
                "Ghi chú",
                "Lý do",
            ]
            fields = [
                "group",
                "start_time_date",
                "start_time_time",
                "customer_name",
                "customer_phone_number",
                "type",
                "technician",
                "doctor",
                "state",
                "note",
                "examination_reason",
            ]
            extra_date_fields = ["start_time_date", "start_time_time"]
            other_format_times = {"start_time_time": "%H:%M:%S"}
            selection_fields = {
                "type": APPOINTMENT_TYPE_DICT,
                "state": APPOINTMENT_STATE_DICT,
            }
            reference_fields = {
                "group": "customer_id.group_id.name",
                "start_time_date": "time_slot_id.start_time",
                "start_time_time": "time_slot_id.start_time",
                "customer_name": "customer_id.name",
                "customer_phone_number": "customer_id.mobile",
                "doctor": "doctor_id.name",
                "technician": "technician_id.name",
                "examination_reason": "examination_reason",
            }
            result = ZAppointmentUtils.export_data(
                queryset,
                headings,
                fields,
                filename,
                extra_date_fields,
                selection_fields,
                reference_fields,
                other_format_times,
            )
            return ResponseUtils.res(result)
        except Exception as e:
            return ResponseUtils.err(e)
