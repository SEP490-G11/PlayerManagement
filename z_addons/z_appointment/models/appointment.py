from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons.z_appointment.helpers.constants import (
    APPOINTMENT_TYPE_CHOICES,
    AppointmentType,
    BOOKING_TYPE_CHOICES,
    BookingType,
    APPOINTMENT_STATE_CHOICES,
    AppointmentState,
    AppointmentErrorCode,
    APPOINTMENT_PRINTING_TYPES,
    AppointmentPrintingType,
    FLOOR_ENUM,
)
from odoo.addons.z_web.helpers.model_utils import ZModelUtils
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_web.helpers.constants import (
    STANDARD_TIME_FORMAT,
    DISPLAY_TIME_SLOT_FORMAT,
)
from datetime import timedelta
from odoo.exceptions import ValidationError


class ZAppointment(models.Model):
    _name = "z_appointment.appointment"
    _rec_name = "title"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Appointment"
    _order = "booking_date desc"

    title = fields.Char(string="Title", compute="_compute_title")
    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        domain="[('is_customer','=', True)]",
        required=True,
    )
    pancake_user_id = fields.Char("Pancake User Id")
    doctor_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Doctor",
        domain="[('is_doctor','=', True)]",
        required=True,
        tracking=True,
    )
    technician_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Technician",
        domain="[('bookable','=', True)]",
        tracking=True,
    )
    time_slot_id = fields.Many2one(
        comodel_name="z_hr.time_slot", string="Time slot", required=True, tracking=True
    )

    customer_detail_widget = fields.Json(
        "Khách hàng", related="customer_id.customer_detail_widget"
    )
    time_slot_start_time = fields.Datetime(
        related="time_slot_id.start_time", store=True
    )
    display_start_time = fields.Char(
        string="Start time", compute="_compute_display_start_time"
    )
    booking_date = fields.Date(
        string="Date", compute="_compute_booking_date", store=True
    )
    booking_time = fields.Char(
        string="Time", compute="_compute_booking_time", store=False
    )
    place_id = fields.Many2one(
        "z_place.place", string="Places", related="time_slot_id.place_id", store=True
    )
    type = fields.Selection(
        APPOINTMENT_TYPE_CHOICES, default=AppointmentType.RE_EXAMINATION, tracking=True
    )
    state = fields.Selection(
        APPOINTMENT_STATE_CHOICES,
        default=AppointmentState.NOT_YET_ARRIVED,
        tracking=True,
    )
    booking_type = fields.Selection(
        BOOKING_TYPE_CHOICES, default=BookingType.BY_DATE, tracking=True
    )
    overbook = fields.Boolean("Overbook", default=False, tracking=True)
    examination_reason = fields.Text("Examination reason")
    examination_code = fields.Char("Examintaion Code")
    note = fields.Text("Note")
    customer_gender = fields.Selection(
        related="customer_id.gender",
        store=False,
        related_sudo=False,
    )
    customer_gender_field = fields.Char(
        string="Gender", compute="_compute_customer_gender_field", store=True
    )
    customer_date = fields.Date(
        related="customer_id.date", store=False, related_sudo=False
    )
    customer_mobile = fields.Char(
        related="customer_id.mobile", store=False, related_sudo=False
    )
    customer_note = fields.Html(
        "Customer note", related="customer_id.comment", store=False, related_sudo=False
    )
    appointment_note = fields.Text("Appoint Note")
    floor = fields.Selection(FLOOR_ENUM, string="Floor")
    has_took_examination = fields.Boolean("Has took examination", default=False)
    printing_type = fields.Selection(
        APPOINTMENT_PRINTING_TYPES,
        default=AppointmentPrintingType.VIVISION_KID,
        tracking=True,
    )

    finish_time = fields.Datetime(
        string="Time Finish Appointment",
        required=False,
        store=True,
        compute="_compute_finish_time",
    )

    has_sent_zns_finish_time = fields.Boolean("Has sent zns finish time", default=True)

    @api.depends("customer_gender")
    def _compute_customer_gender_field(self):
        for rec in self:
            rec.customer_gender_field = (
                _("Male") if rec.customer_gender == "male" else _("Female")
            )

    customer_age = fields.Integer(
        string="Customer Age",
        related="customer_id.age",
        store=False,
        related_sudo=False,
    )

    customer_age_display = fields.Char(
        string="Customer Age",
        related="customer_id.display_age",
        store=False,
        related_sudo=False,
    )
    reexam_count = fields.Integer(
        "Số lần tái khám", compute="_compute_reexam_count", store=True
    )

    @api.depends("customer_id")
    def _compute_reexam_count(self):
        for rec in self:
            appointments = self.search([("customer_id", "=", rec.customer_id.id)])
            rec.reexam_count = len(appointments) - 1

    @api.depends("customer_id", "display_start_time")
    def _compute_title(self):
        for rec in self:
            rec.title = f"{rec.customer_id.name} - {rec.display_start_time}"

    @api.depends("time_slot_start_time")
    def _compute_display_start_time(self):
        for rec in self:
            rec.display_start_time = ZUtils.format_datetime(
                rec.time_slot_id.start_time, DISPLAY_TIME_SLOT_FORMAT
            )

    @api.depends("time_slot_start_time")
    def _compute_booking_date(self):
        for rec in self:
            dt = rec.time_slot_id.start_time
            rec.booking_date = datetime(dt.year, dt.month, dt.day)

    @api.depends("time_slot_start_time")
    def _compute_booking_time(self):
        for rec in self:
            rec.booking_time = ZUtils.format_datetime(
                rec.time_slot_id.start_time, STANDARD_TIME_FORMAT
            )

    @api.depends("state")
    def _compute_finish_time(self):
        for rec in self:
            if rec.state == AppointmentState.FINISHED and not rec.finish_time:
                rec.finish_time = fields.Datetime.now()
                rec.has_sent_zns_finish_time = False

    def _get_appointment_by_id(self, appointment_id):
        return ZModelUtils.get_record_by_id(
            self, appointment_id, AppointmentErrorCode.APPOINTMENT_DOES_NOT_EXIST
        )

    def _get_appointments_by_doctor_id_and_start_time(self, doctor_id: int, start_time):
        return self.search(
            [
                ("doctor_id", "=", doctor_id),
                ("time_slot_id.start_time", "=", start_time),
            ]
        )

    @api.depends("floor", "state")
    def _compute_state_and_floor(self):
        for rec in self:
            rec.state_and_floor = {"state": rec.state, "floor": rec.floor}

    def write(self, vals):
        if vals.get("state") == "1" and (
            self.has_comprehensive
            or self.has_lens
            or self.has_re_lens
            or self.has_vision
            or self.has_binocular_vision
            or self.has_glass_order
            or self.has_invoice
        ):
            raise ValidationError(
                "Không thể cập cập nhật trạng thái chưa đến cho lượt khám đã đến khám"
            )
        return super().write(vals)
