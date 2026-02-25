# -*- coding: utf-8 -*-
import re
import json
import logging
from odoo.addons.z_web.helpers.response import ResponseUtils
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta, time
from odoo.addons.z_web.helpers.constants import (
    ErrorCode,
)

_logger = logging.getLogger(__name__)


class ZCrmZQueue(models.Model):
    _name = "z.crm.queue"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "CRM Queue"
    _rec_name = "name"

    name = fields.Char(string="Name", required=False)
    method = fields.Selection(
        [("task", _("Task")), ("zns", _("Zalo"))], string="Method", default="task"
    )
    execute_time = fields.Datetime(string="Execute Time")
    error_logs = fields.Text(string="Logs")
    partner_id = fields.Many2one(string="Customer", comodel_name="res.partner")
    status = fields.Boolean(string="Status", default=False)
    zns_template_ids = fields.One2many(
        "z.crm.zns.template.queue", "crm_queue_id", "ZNS Templates"
    )
    task_template_ids = fields.One2many(
        "z.crm.task.template.queue", "crm_queue_id", "Task Templates"
    )
    record_id = fields.Integer("Model ID")
    model_name = fields.Char(string="Model Name")
    # state will selection success or fail or pending
    state = fields.Selection(
        [("success", "Success"), ("fail", "Fail"), ("pending", "Pending")],
        string="State",
        default="pending",
    )
    msg_id = fields.Char(string="MsgID", compute="_compute_msg_id", store=True)

    template_name = fields.Char(string="Template", compute="_compute_template_name")

    @api.depends(
        "zns_template_ids",
        "zns_template_ids.msg_id",
    )
    def _compute_msg_id(self):
        for record in self:
            record.msg_id = (
                record.zns_template_ids[0].msg_id if record.zns_template_ids else ""
            )

    @api.depends(
        "method",
        "task_template_ids",
        "zns_template_ids",
        "zns_template_ids.name",
        "task_template_ids.name",
    )
    def _compute_template_name(self):
        for record in self:
            if record.method == "task":
                record.template_name = (
                    record.task_template_ids[0].name if record.task_template_ids else ""
                )
            elif record.method == "zns":
                record.template_name = (
                    record.zns_template_ids[0].name if record.zns_template_ids else ""
                )

    # TICKET

    def create_crm_queue_task_template_reexamination(
        self,
        name=False,
        method="task",
        partner_id=False,
        task_template_code=False,
        reexamination_date=False,
        record_id=False,
        model_name=False,
    ):
        if not reexamination_date:
            return
        task_template_ids = []
        data = {}
        reexamination_date_to_be_execute = reexamination_date - timedelta(days=2)
        if isinstance(reexamination_date, date):
            reexamination_date = reexamination_date.strftime("%d/%m/%Y")

        # Chuẩn bị dữ liệu để tạo bản ghi mới
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.task.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": f"Nhắc lịch tái khám cho khách hàng {partner.name or ''} ngày {reexamination_date}",
                    "content": f"Lịch tái khám của khách hàng {partner.name or ''} là {reexamination_date}. Vui lòng liên hệ khách hàng để hỗ trợ đặt lịch.",
                    "code": f"{task_template.code or ''}",
                    "execute_time": datetime.combine(
                        reexamination_date_to_be_execute, datetime.min.time()
                    ).replace(hour=2, minute=0, second=0),
                    "function_name": "create_ticket_for_reexamination",
                }

        values = {
            "name": name,
            "method": method,
            "partner_id": partner_id.id,
            "task_template_ids": ([(0, 0, data)] if data else False),
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    def create_crm_queue_task_template_glass_care(
        self,
        name=False,
        method="task",
        partner_id=False,
        task_template_code=False,
        glass_care_date=False,
        record_id=False,
        model_name=False,
    ):
        task_template_ids = []
        data = {}

        # Ensure glass_care_date is a datetime object
        if isinstance(glass_care_date, datetime):
            # Add 7 days to glass_care_date
            glass_care_date = glass_care_date + timedelta(days=7)

            # Set the time to 10:00 AM before converting to string
            glass_care_date = glass_care_date.replace(hour=2, minute=0, second=0)

            # Convert the new date to string in the format dd/mm/YYYY
            glass_care_date_7 = glass_care_date.strftime("%d/%m/%Y")

        else:
            glass_care_date_7 = False  # Handle case where no valid date is provided

        # Prepare data for creating a new record
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.task.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "code": f"{task_template.code or ''}",
                    "name": f"Chăm sóc kính: {partner.name or ''}",
                    "content": f"Ngày chăm sóc kính của {partner.name or ''} là {glass_care_date_7}. Vui lòng liên hệ khách hàng để hỏi thăm tình trạng đeo kính",
                    "execute_time": glass_care_date,
                    "function_name": "create_ticket_for_glass_order",  # Use the datetime object for execute_time
                }

        values = {
            "name": name,
            "method": method,
            "partner_id": partner_id.id,
            "task_template_ids": [(0, 0, data)] if data else False,
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    def create_crm_queue_task_template_glass_order(
        self,
        name=False,
        method="task",
        partner_id=False,
        task_template_code=False,
        glass_care_date=False,
        record_id=False,
        model_name=False,
    ):
        task_template_ids = []
        data = {}

        # Ensure glass_care_date is a datetime object and set time to 00:00:00
        if isinstance(glass_care_date, datetime):
            # Set hour, minute, second to 0 (midnight)
            glass_care_date = glass_care_date.replace(hour=0, minute=0, second=0)
            # Convert to string format after setting the time
            glass_care_date_str = glass_care_date.strftime("%d/%m/%Y")
        else:
            glass_care_date_str = (
                False  # Handle case where no valid datetime is provided
            )

        # Prepare data for creating a new record
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.task.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": f"Chăm sóc khách hàng mua {partner.name or ''} kính Ortho-k",
                    "content": f"Check thời gian kính về với hàng và thông báo lịch trình tới khách hàng.",
                    "code": f"{task_template.code or ''}",
                    "execute_time": (glass_care_date if glass_care_date else False),
                    "function_name": "create_ticket_for_glass_order",  # Use the datetime object for execute_time
                }

        values = {
            "name": name,
            "method": method,
            "partner_id": partner_id.id,
            "task_template_ids": [(0, 0, data)] if data else False,
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    def create_crm_queue_task_template_care_after_exam(
        self,
        name=False,
        method="task",
        partner_id=False,
        task_template_code=False,
        placed_date=False,
        after_placed_date=False,
        record_id=False,
        model_name=False,
    ):
        task_template_ids = []
        data = {}
        placed_after_n_date = False

        if isinstance(placed_date, datetime) or isinstance(placed_date, date):
            placed_date = placed_date + timedelta(days=after_placed_date)
            placed_after_n_date = placed_date.strftime("%d/%m/%Y")

        # Chuẩn bị dữ liệu để tạo bản ghi mới
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.task.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": f"Chăm sóc phần mềm khách hàng {partner.name or ''} ngày {placed_after_n_date}",
                    "content": f"Hỗ trợ khách hàng {partner.name or ''} sau {after_placed_date} ngày sử dụng",
                    "code": f"{task_template.code or ''}",
                    "execute_time": datetime.combine(
                        placed_date, datetime.min.time()
                    ).replace(hour=9, minute=30, second=0),
                    "function_name": "create_ticket_for_care_after_exam",
                }

        values = {
            "name": name,
            "method": method,
            "partner_id": partner_id.id,
            "task_template_ids": ([(0, 0, data)] if data else False),
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    # ZALO
    def create_crm_queue_zns_template_confirm_appointment_18plus(
        self,
        method="zns",
        partner_id=False,
        task_template_code=False,
        create_date=False,
        exam_date=False,
        exam_hour=False,
        exam_place=False,
        record_id=False,
        model_name=False,
    ):
        try:
            task_template_ids = []
            data = {}
            if isinstance(exam_date, date):
                exam_date = exam_date.strftime("%d/%m/%Y")

            # Chuẩn bị dữ liệu để tạo bản ghi mới
            if task_template_code:
                # Search for the task template by code
                task_template = self.env["z.crm.zns.template"].search(
                    [("code", "=", task_template_code)], limit=1
                )
                if task_template:
                    partner = self.env["res.partner"].search(
                        [("id", "=", partner_id.id)], limit=1
                    )
                    data = {
                        "name": "Xác nhận lịch hẹn",
                        "body": f"<p>Xác nhận lịch hẹn <br>Quý khách thân mến!<strong>vivision</strong> xác nhận thông tin đặt lịch khám của quý khách {partner.name or ''} như sau:<br>Mã khách hàng: {partner.code or ''}<br>Thời gian khám: {exam_date + ' ' + exam_hour}<br>Địa chỉ cơ sở khám: {exam_place}<br>Trường hợp không thể tới phòng khám theo đúng lịch hẹn, quý khách vui lòng liên hệ hotline của vivision để thay đổi lịch.Cảm ơn quý khách hàng đã tin tưởng và lựa chọn vivision!CTA: Quan tâm OA<br></p>",
                        "code": f"{task_template.code or ''}",
                        "execute_time": create_date,
                    }
                else:
                    _logger.error("ZNS not found template: %s", task_template_code)

            values = {
                "method": method,
                "partner_id": partner_id.id,
                "zns_template_ids": ([(0, 0, data)] if data else False),
                "record_id": record_id,
                "model_name": model_name,
                "status": True,
            }

            # Tạo bản ghi mới trong z.crm.queue
            crm_queue = self.sudo().create(values)

            return crm_queue
        except Exception:
            return ResponseUtils.err(code=ErrorCode.INTERNAL_SERVER_ERROR)

    def create_crm_queue_zns_template_confirm_appointment_18(
        self,
        method="zns",
        partner_id=False,
        task_template_code=False,
        create_date=False,
        exam_date=False,
        exam_hour=False,
        exam_place=False,
        record_id=False,
        model_name=False,
    ):
        task_template_ids = []
        data = {}
        if isinstance(exam_date, date):
            exam_date = exam_date.strftime("%d/%m/%Y")

        # Chuẩn bị dữ liệu để tạo bản ghi mới
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.zns.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": "Xác nhận lịch hẹn",
                    "body": f"<p>Xác nhận lịch hẹn <br>Quý khách thân mến!<strong>vivision</strong> xác nhận thông tin đặt lịch khám của quý khách {partner.name or ''} như sau:<br>Mã khách hàng: {partner.code or ''}<br>Thời gian khám: {exam_date + ' '+ exam_hour}<br>Địa chỉ cơ sở khám: {exam_place}<br>Trường hợp không thể tới phòng khám theo đúng lịch hẹn, quý khách vui lòng liên hệ hotline của vivision để thay đổi lịch.Cảm ơn quý khách hàng đã tin tưởng và lựa chọn vivision!CTA: Quan tâm OA<br></p>",
                    "code": f"{task_template.code or ''}",
                    "execute_time": create_date,
                }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": ([(0, 0, data)] if data else False),
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    def create_crm_queue_zns_template_retell_registration_18plus(
        self,
        method="zns",
        partner_id=False,
        task_template_code=False,
        create_date=False,
        exam_date=False,
        exam_hour=False,
        exam_place=False,
        record_id=False,
        model_name=False,
    ):
        task_template_ids = []
        data = {}
        if isinstance(exam_date, date):
            exam_date = exam_date.strftime("%d/%m/%Y")

        # Chuẩn bị dữ liệu để tạo bản ghi mới
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.zns.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": "Nhắc lại lịch đã đăng kí",
                    "body": f"<p>vivision xin chào!<br>Khách hàng {partner.name or ''} với mã {partner.code or ''} có lịch hẹn thăm khám mắt vào {exam_hour} {exam_date} tại cơ sở {exam_place}.<br>Quý khách vui lòng đến trước 10 phút để chuẩn bị trước khi vào khám.<br>Vivision luôn sẻ chia cùng quý khách hàng trong hành trình bảo vệ đôi mắt. CTA: Liên hệ CSKH<br></p>",
                    "code": f"{task_template.code or ''}",
                    "execute_time": create_date,
                }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": ([(0, 0, data)] if data else False),
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    def create_crm_queue_zns_template_retell_registration_18(
        self,
        method="zns",
        partner_id=False,
        task_template_code=False,
        create_date=False,
        exam_date=False,
        exam_hour=False,
        exam_place=False,
        record_id=False,
        model_name=False,
    ):
        task_template_ids = []
        data = {}
        if isinstance(exam_date, date):
            exam_date = exam_date.strftime("%d/%m/%Y")

        # Chuẩn bị dữ liệu để tạo bản ghi mới
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.zns.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": "Nhắc lại lịch đã đăng kí",
                    "body": f"<p>vivision xin chào!<br>Khách hàng {partner.name or ''} với mã {partner.code or ''} có lịch hẹn thăm khám mắt vào {exam_hour} {exam_date} tại cơ sở {exam_place}.<br>Quý khách vui lòng đến trước 10 phút để chuẩn bị trước khi vào khám.<br>Vivision luôn sẻ chia cùng quý khách hàng trong hành trình bảo vệ đôi mắt. CTA: Liên hệ CSKH<br></p>",
                    "code": f"{task_template.code or ''}",
                    "execute_time": create_date,
                }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": ([(0, 0, data)] if data else False),
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    def create_crm_queue_zns_template_glass_order_18(
        self,
        method="zns",
        partner_id=False,
        task_template_code=False,
        date=False,
        order_date=False,
        type=False,
        recipient=False,
        address=False,
        place=False,
        phone=False,
        record_id=False,
        model_name=False,
    ):
        task_template_ids = []
        data = {}
        # Chuẩn bị dữ liệu để tạo bản ghi mới
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.zns.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": "Hẹn lấy kính",
                    "body": f"<p>Xác nhận đơn hàngQuý khách thân mến !Đơn kính của khách hàng {partner.name or ''} với mã {partner.code or ''} đã được xác nhận trên hệ thống của vivision. Thông tin đặt hàng như sau:<br>Ngày dự kiến hoàn thành: {order_date.strftime('%d/%m/%Y')}Hình thức nhận: {'Nhận tại nhà' if type=='delivery' else 'Nhận tại phòng khám'}Người nhận: {recipient}Địa chỉ: {address if type=='delivery' else place}Số điện thoại: {phone}<br>Cảm ơn quý khách đã sử dụng dịch vụ của vivision!CTA: Liên hệ CSKH<br></p>",
                    "code": f"{task_template.code or ''}",
                    "execute_time": date,
                }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": ([(0, 0, data)] if data else False),
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    def create_crm_queue_zns_template_glass_order_18plus(
        self,
        method="zns",
        partner_id=False,
        task_template_code=False,
        date=False,
        order_date=False,
        type=False,
        recipient=False,
        address=False,
        place=False,
        phone=False,
        record_id=False,
        model_name=False,
    ):
        task_template_ids = []
        data = {}
        # Chuẩn bị dữ liệu để tạo bản ghi mới
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.zns.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": "Hẹn lấy kính",
                    "body": f"<p>Xác nhận đơn hàng Quý khách thân mến !Đơn kính của khách hàng {partner.name or ''} với mã {partner.code or ''} đã được xác nhận trên hệ thống của vivision. Thông tin đặt hàng như sau:<br>Ngày dự kiến hoàn thành: {order_date.strftime('%d/%m/%Y')}Hình thức nhận: {'Nhận tại nhà' if type=='delivery' else 'Nhận tại phòng khám'}Người nhận: {recipient}Địa chỉ: {address if type=='delivery' else place}Số điện thoại: {phone}<br>Cảm ơn quý khách đã sử dụng dịch vụ của vivision!CTA: Liên hệ CSKH<br></p>",
                    "code": f"{task_template.code or ''}",
                    "execute_time": date,
                }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": ([(0, 0, data)] if data else False),
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    def create_crm_queue_zns_template_install_service_18(
        self,
        method="zns",
        partner_id=False,
        task_template_code=False,
        date=False,
        tracking_date=False,
        combo_name=False,
        phone=False,
        record_id=False,
        model_name=False,
    ):
        task_template_ids = []
        data = {}
        # Chuẩn bị dữ liệu để tạo bản ghi mới
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.zns.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": "Thông báo ngày cài đặt dự kiến phần mềm AMB và huấn luyện thị giác 2M",
                    "body": f"<p>Thông báo cài đặt phần mềm Bé {partner.name or ''}  với mã {partner.code or ''} đã mua {combo_name}. vivision thông báo lịch trình cài đặt như sau:<br>Ngày cài đặt: {tracking_date.strftime('%d/%m/%Y')}Hình thức cài: UltraviewerSố điện thoại: {phone}<br>Cảm ơn quý khách đã sử dụng dịch vụ của vivision!CTA: Liên hệ CSKH<br></p>",
                    "code": f"{task_template.code or ''}",
                    "execute_time": date,
                }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": ([(0, 0, data)] if data else False),
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    def create_crm_queue_zns_template_install_service_18plus(
        self,
        method="zns",
        partner_id=False,
        task_template_code=False,
        date=False,
        tracking_date=False,
        combo_name=False,
        phone=False,
        record_id=False,
        model_name=False,
    ):
        task_template_ids = []
        data = {}
        # Chuẩn bị dữ liệu để tạo bản ghi mới
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.zns.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": "Thông báo ngày cài đặt dự kiến phần mềm AMB và huấn luyện thị giác 2M",
                    "body": f"<p>Thông báo cài đặt phần mềmBé {partner.name or ''}  với mã {partner.code or ''} đã mua {combo_name}. vivision thông báo lịch trình cài đặt như sau:<br>Ngày cài đặt: {tracking_date.strftime('%d/%m/%Y')}Hình thức cài: UltraviewerSố điện thoại: {phone}<br>Cảm ơn quý khách đã sử dụng dịch vụ của vivision!CTA: Liên hệ CSKH<br></p>",
                    "code": f"{task_template.code or ''}",
                    "execute_time": date,
                }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": ([(0, 0, data)] if data else False),
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)

        return crm_queue

    # zns for vision
    def create_crm_queue_zns_template_review_appointment_vision(
        self,
        method="zns",
        partner_id=False,
        task_template_code=False,
        date=False,
        exam_date=False,
        record_id=False,
        model_name=False,
    ):
        data = {}
        tomorrow = datetime.today() + timedelta(days=1)
        execute_time = datetime.combine(tomorrow, time(12, 0, 0))
        # Chuẩn bị dữ liệu để tạo bản ghi mới
        if task_template_code:
            # Search for the task template by code
            task_template = self.env["z.crm.zns.template"].search(
                [("code", "=", task_template_code)], limit=1
            )
            if task_template:
                partner = self.env["res.partner"].search(
                    [("id", "=", partner_id.id)], limit=1
                )
                data = {
                    "name": "Khảo sát chất lượng dịch vụ",
                    "body": f"Đánh giá trải nghiệm cùng vivision! Cám ơn quý khách {partner.name or ''} với mã hồ sơ {partner.code or ''} đã tin tưởng lựa chọn dịch vụ khám mắt của VIVISION. Hãy đánh giá trải nghiệm cùng VIVISION để chúng tôi không ngừng nâng cao chất lượng dịch vụ nhé!",
                    "code": f"{task_template.code or ''}",
                    "execute_time": execute_time,
                }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": ([(0, 0, data)] if data else False),
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)
        return crm_queue

    def create_crm_queue_zns_survey_18plus(
        self,
        method="zns",
        partner_id=False,
        task_template_code="zns_421915",
        booking_date=False,
        record_id=False,
        model_name=False,
    ):
        if not partner_id or not booking_date:
            return False

        # Kiểm tra điều kiện ngày gửi (booking_date từ 01-07 hoặc 15-21)
        if not (1 <= booking_date.day <= 7 or 15 <= booking_date.day <= 21):
            return False

        # Tính ngày gửi
        send_date = booking_date + timedelta(days=1)
        send_datetime = datetime.combine(send_date, time(hour=2, minute=0, second=0))

        # Load template ZNS ID 421915
        task_template = self.env["z.crm.zns.template"].search(
            [("code", "=", task_template_code)], limit=1
        )
        data = {
            "name": "Khảo sát chất lượng dịch vụ",
            "body": f"Đánh giá trải nghiệm cùng VIVISION!VIVISION chào bạn {partner_id.name or ''}. Cám ơn bạn với số điện thoại {partner_id.mobile or ''} đã tin tưởng lựa chọn dịch vụ của VIVISION cho hành trình chăm sóc đôi mắt của mình. Chúng tôi rất vinh hạnh được đồng hành cùng bạn. Vui lòng đánh giá trải nghiệm cùng VIVISION để chúng tôi không ngừng nâng cao chất lượng dịch vụ nhé!",
            "code": task_template.code,
            "execute_time": send_datetime,
        }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": [(0, 0, data)],
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)
        return crm_queue

    def create_crm_queue_zns_survey_18(
        self,
        method="zns",
        partner_id=False,
        task_template_code="zns_422789",
        booking_date=False,
        record_id=False,
        model_name=False,
    ):
        if not partner_id or not booking_date:
            return False

        # Kiểm tra điều kiện ngày gửi (booking_date từ 01-07 hoặc 15-21)
        if not (1 <= booking_date.day <= 7 or 15 <= booking_date.day <= 21):
            return False

        # Tính ngày gửi
        send_date = booking_date + timedelta(days=1)
        send_datetime = datetime.combine(send_date, time(hour=2, minute=0, second=0))

        # Load template ZNS ID 421915
        task_template = self.env["z.crm.zns.template"].search(
            [("code", "=", task_template_code)], limit=1
        )
        data = {
            "name": "Khảo sát chất lượng dịch vụ",
            "body": f"Đánh giá trải nghiệm cùng VIVISION KID!VIVISION KID chào bố mẹ. Cám ơn bố mẹ số điện thoại {partner_id.mobile or ''} đã tin tưởng lựa chọn dịch vụ của VIVISION KID cho hành trình chăm sóc đôi mắt của con {partner_id.name or ''}. Chúng tôi rất vinh hạnh được đồng hành cùng gia đình mình. Nhà mình vui lòng đánh giá trải nghiệm cùng VIVISION để chúng tôi không ngừng nâng cao chất lượng dịch vụ nhé",
            "code": task_template.code,
            "execute_time": send_datetime,
        }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": [(0, 0, data)],
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)
        return crm_queue

    def create_crm_queue_zns_nps_survey_18plus(
        self,
        method="zns",
        partner_id=False,
        task_template_code="zns_422787",
        booking_date=False,
        record_id=False,
        model_name=False,
    ):
        if not partner_id or not booking_date:
            return False

        if not (8 <= booking_date.day <= 15 or 22 <= booking_date.day <= 31):
            return False

        # Tính ngày gửi
        send_date = booking_date + timedelta(days=1)
        send_datetime = datetime.combine(send_date, time(hour=2, minute=0, second=0))

        # Load template ZNS ID 421915
        task_template = self.env["z.crm.zns.template"].search(
            [("code", "=", task_template_code)], limit=1
        )
        data = {
            "name": "Đánh giá điểm NPS",
            "body": f"Giới thiệu VIVISION tới bạn bè, người thân!VIVISION chào bạn {partner_id.name or ''}. Cảm ơn bạn số điện thoại {partner_id.mobile or ''} đã tin tưởng lựa chọn VIVISION cho hành trình chăm sóc đôi mắt của mình. Chúng tôi rất vinh hạnh được đồng hành cùng bạn. Vui lòng đánh giá mức độ sẵn sàng giới thiệu VIVISION tới bạn bè người thân cùng chúng tôi nhé. Mọi ý kiến đóng góp của bạn sẽ giúp chúng tôi hoàn thiện chất lượng phục vụ tốt hơn trong tương lai.",
            "code": task_template.code,
            "execute_time": send_datetime,
        }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": [(0, 0, data)],
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)
        return crm_queue

    def create_crm_queue_zns_nps_survey_18(
        self,
        method="zns",
        partner_id=False,
        task_template_code="zns_421920",
        booking_date=False,
        record_id=False,
        model_name=False,
    ):
        if not partner_id or not booking_date:
            return False

        if not (8 <= booking_date.day <= 15 or 22 <= booking_date.day <= 31):
            return False

        # Tính ngày gửi
        send_date = booking_date + timedelta(days=1)
        send_datetime = datetime.combine(send_date, time(hour=2, minute=0, second=0))

        # Load template ZNS ID 421915
        task_template = self.env["z.crm.zns.template"].search(
            [("code", "=", task_template_code)], limit=1
        )
        data = {
            "name": "Đánh giá điểm NPS",
            "body": f"Giới thiệu VIVISION tới bạn bè, người thân!VIVISION KID chào bố mẹ. Cảm ơn nhà mình đã tin tưởng lựa chọn VIVISION KID cho hành trình chăm sóc đôi mắt của con {partner_id.name or ''} với số điện thoại {partner_id.mobile or ''}. Cô chú rất vinh hạnh được đồng hành cùng gia đình mình. Vui lòng đánh giá mức độ sẵn sàng giới thiệu VIVISION KID tới bạn bè người thân cùng cô chú nhé. Mọi ý kiến đóng góp của bố mẹ sẽ giúp chúng tôi hoàn thiện chất lượng hơn.",
            "code": task_template.code,
            "execute_time": send_datetime,
        }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": [(0, 0, data)],
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)
        return crm_queue

    def get_pending_and_active_status_queues(self):
        return self.search([("status", "=", True), ("state", "in", ["pending", "fail"])])

    def handle_pending_and_active_status_queues(self):
        for queue in self.get_pending_and_active_status_queues():
            if queue.method == "task":
                for task_template in queue.task_template_ids:
                    task_template.handle_task_template()
            if queue.method == "zns":
                # get length cua queue.zns_template_ids
                totalLines = len(queue.zns_template_ids)
                totalSuccess = 0
                totalFail = 0
                for zns_template in queue.zns_template_ids:
                    if zns_template.status == "success":
                        totalSuccess = totalSuccess + 1
                    if zns_template.status == "fail":
                        totalFail = totalFail + 1
                    # chi chay cho nhung template chua success, retry < 3 va thoi gian excute time < now
                    if (
                        zns_template.execute_time <= fields.Datetime.now()
                        and zns_template.status != "success"
                        and zns_template.number_of_run_queues < 3
                    ):
                        status = zns_template.handle_zns_template()
                        if status == "success":
                            totalSuccess = totalSuccess + 1
                        if (
                            zns_template.number_of_run_queues == 2
                            and zns_template.status == "fail"
                        ):
                            totalFail = totalFail + 1

                # reget lai new data after update to check all status true of zns_template_ids
                is_finish = totalLines == (totalSuccess + totalFail)
                if is_finish and totalFail:
                    # update queue ve fail
                    queue.state = "fail"
                if is_finish and totalFail == 0:
                    # update queue ve success
                    queue.state = "success"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "seq.z.crm_request"
            ) or _("Mới")
        return super(ZCrmZQueue, self).create(vals)

    def create_crm_queue_zns_appointment_confirm_18(
        self,
        method="zns",
        partner_id=False,
        task_template_code="zns_429776",
        booking_date=False,
        booking_time=False,
        date=False,
        record_id=False,
        model_name=False,
    ):
        if not partner_id or not booking_date or not booking_time:
            return False

        # Load template ZNS ID 421915
        task_template = self.env["z.crm.zns.template"].search(
            [("code", "=", task_template_code)], limit=1
        )
        if task_template:
            partner = self.env["res.partner"].search(
                [("id", "=", partner_id.id)], limit=1
            )
            data = {
                "name": "Xác nhận lịch hẹn",
                "body": f"VIVISION KID xác nhận lịch hẹn Xác nhận lịch hẹn bạn {partner.name or ''} với số điện thoại {partner.mobile or ''}. Lưu ý: Bố mẹ nhớ mang theo kết quả khám cũ và đến trước 10 phút. Bố mẹ có thể gửi xe máy ở trước cửa phòng khám và ô tô ở phía đối diện phòng khám. Nếu trước cửa hết chỗ, bố mẹ có thể gửi ở đối diện phòng khám và vui lòng cung cấp vé gửi xe khi thanh toán để được hỗ trợ chi phí nhé!Thời gian khám : {booking_time or ''} {booking_date or ''} Địa chỉ cơ sở khám : 514 Bạch Mai, Hai Bà Trưng, Hà Nội CTA: Quan tâm OA",
                "code": task_template.code,
                "execute_time": date,
            }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": [(0, 0, data)],
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)
        return crm_queue

    def create_crm_queue_zns_appointment_confirm_18plus(
        self,
        method="zns",
        partner_id=False,
        task_template_code="zns_429779",
        booking_date=False,
        booking_time=False,
        date=False,
        record_id=False,
        model_name=False,
    ):
        if not partner_id or not booking_date or not booking_time:
            return False

        # Load template ZNS ID 421915
        task_template = self.env["z.crm.zns.template"].search(
            [("code", "=", task_template_code)], limit=1
        )
        if task_template:
            partner = self.env["res.partner"].search(
                [("id", "=", partner_id.id)], limit=1
            )
            data = {
                "name": "Xác nhận lịch hẹn",
                "body": f"VIVISION KID xác nhận lịch hẹn Xác nhận lịch hẹn bạn {partner.name or ''} với số điện thoại {partner.mobile or ''}. Lưu ý: Bạn nhớ mang theo kết quả khám cũ và đến trước 10 phút. Bạn có thể gửi xe máy ở trước cửa phòng khám và ô tô ở phía đối diện phòng khám. Nếu trước cửa hết chỗ, bạn có thể gửi ở đối diện phòng khám và vui lòng cung cấp vé gửi xe khi thanh toán để được hỗ trợ chi phí nhé. Thời gian khám : {booking_time or ''} {booking_date or ''} Địa chỉ cơ sở khám : 514 Bạch Mai, Hai Bà Trưng, Hà Nội CTA: Quan tâm OA",
                "code": task_template.code,
                "execute_time": date,
            }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": [(0, 0, data)],
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)
        return crm_queue

    def create_crm_queue_zns_appointment_remind_18plus(
        self,
        method="zns",
        partner_id=False,
        task_template_code="zns_399184",
        booking_date=False,
        booking_time=False,
        record_id=False,
        model_name=False,
    ):
        today = fields.Date.today()
        days_diff = (booking_date - today).days
        if 0 <= days_diff <= 2:
            return False
        if not partner_id or not booking_date or not booking_time:
            return False
        reminder_date = datetime.combine(booking_date, time(2, 0)) - timedelta(days=2)

        task_template = self.env["z.crm.zns.template"].search(
            [("code", "=", task_template_code)], limit=1
        )
        if task_template:
            partner = self.env["res.partner"].search(
                [("id", "=", partner_id.id)], limit=1
            )
            data = {
                "name": "Nhắc lại lịch đã đăng kí",
                "body": f"Thông báo lịch khám Quý khách {partner.name or ''} với mã khách hàng {partner.code or ''} có lịch hẹn khám vào lúc {booking_time or ''} {booking_date or ''} tại địa ch 514 Bạch Mai, Hai Bà Trưng, Hà Nội. Quý khách vui lòng đến đúng giờ hẹn để chuẩn bị trước khi vào khám. VIVISION sẵn sàng sẻ chia cùng quý khách hàng trong hành trình bảo vệ sức khỏe mắt. CTA: Liên hệ CSKH",
                "code": task_template.code,
                "execute_time": reminder_date,
            }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": [(0, 0, data)],
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)
        return crm_queue

    def create_crm_queue_zns_appointment_remind_18(
        self,
        method="zns",
        partner_id=False,
        task_template_code="zns_399185",
        booking_date=False,
        booking_time=False,
        record_id=False,
        model_name=False,
    ):
        today = fields.Date.today()
        days_diff = (booking_date - today).days
        if 0 <= days_diff <= 2:
            return False
        if not partner_id or not booking_date or not booking_time:
            return False
        reminder_date = datetime.combine(booking_date, time(2, 0)) - timedelta(days=2)

        task_template = self.env["z.crm.zns.template"].search(
            [("code", "=", task_template_code)], limit=1
        )
        if task_template:
            partner = self.env["res.partner"].search(
                [("id", "=", partner_id.id)], limit=1
            )
            data = {
                "name": "Nhắc lại lịch đã đăng kí",
                "body": f"Thông báo lịch khám Bé {partner.name or ''} với mã hồ sơ {partner.code or ''} có lịch hẹn khám vào lúc {booking_time or ''} {booking_date or ''} tại địa chỉ 514 Bạch Mai, Hai Bà Trưng, Hà Nội. Quý khách vui lòng đưa bé đến đúng giờ hẹn để chuẩn bị trước khi vào khám. VIVISION sẵn sàng sẻ chia cùng quý khách hàng trong hành trình bảo vệ sức khỏe mắt của con. CTA: Liên hệ CSKH",
                "code": task_template.code,
                "execute_time": reminder_date,
            }

        values = {
            "method": method,
            "partner_id": partner_id.id,
            "zns_template_ids": [(0, 0, data)],
            "record_id": record_id,
            "model_name": model_name,
            "status": True,
        }

        # Tạo bản ghi mới trong z.crm.queue
        crm_queue = self.sudo().create(values)
        return crm_queue
