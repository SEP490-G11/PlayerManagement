# -*- coding: utf-8 -*-

from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.addons.z_obstetric.helpers.utils import ZAppointmentUtilsExtend
from odoo.addons.z_web.helpers.constants import ErrorCode
from odoo.addons.z_web.helpers.request import ZRequest
from odoo.addons.z_web.helpers.response import ResponseUtils
from odoo.addons.z_appointment.controllers.appointment_controllers import ZAppointmentController
from odoo.addons.z_appointment.helpers.utils import ZAppointmentUtils

class ZAppointmentControllerExtend(ZAppointmentController):
    @http.route("/z_appointment/appointment", auth="user", methods=["POST"])
    def create_appointment(self, **kw):
        try:
            payload = ZRequest.parse_to_json(kw)
            appointment = ZAppointmentUtilsExtend.create_or_update(http.request, payload)
            return ResponseUtils.res(
                ZAppointmentUtilsExtend.format_detail(appointment), "Đặt lịch thành công"
            )
        except ValidationError as e:
            return ResponseUtils.err(msg=str(e))
        except UserError as code:
            return ResponseUtils.err(code=code)
        except Exception:
            return ResponseUtils.err(code=ErrorCode.INTERNAL_SERVER_ERROR)
    
    # override logic api 'update state' 
    @http.route(
        "/z_appointment/appointment/update_state/<int:id>", auth="user", methods=["PUT"]
    )
    def update_appointment_state(self, **kw):
        try:
            payload = ZRequest.parse_to_json(kw)
            state = payload.get("state")
            is_visit = payload.get("is_visit")
            # update logic need validate when change state
            ZAppointmentUtilsExtend.validate_appointment_state(state, is_visit)
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