# -*- coding: utf-8 -*-
from unidecode import unidecode
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.addons.z_appointment.helpers.constants import (
    APPOINTMENT_TYPE_CHOICES,
    AppointmentType,
    BOOKING_TYPE_CHOICES,
    BookingType,
    APPOINTMENT_STATE_CHOICES,
    AppointmentState,
    APPOINTMENT_PRINTING_TYPES,
    AppointmentPrintingType,
)

class ZAppointment(models.Model):
    _name = "z_appointment.appointment"
    _inherit = ["z_appointment.appointment", "mail.thread", "mail.activity.mixin"]

    gynecological_ids = fields.One2many(
        "z_obstetric.gynecological", "visit_id", "Gynecological", copy=True
    )
    non_speculum_gynecological_ids = fields.One2many(
        "z_obstetric.non_gynecological",
        "visit_id",
        "Non Speculum Gynecological",
        copy=True,
    )
    post_first_tremester_pregnant_ids = fields.One2many(
        "z_obstetric.post_pregnant",
        "visit_id",
        "Post-first Tremester Pregnant",
        copy=True,
    )
    pre_first_tremester_pregnant_ids = fields.One2many(
        "z_obstetric.pre_pregnant",
        "visit_id",
        "Pre-first Tremester Pregnant",
        copy=True,
    )
    ultra_sound_ids = fields.One2many(
        "z_obstetric.ultra_sound",
        "visit_id",
        "Ultra sound",
        copy=True,
    )
    has_gynecological = fields.Boolean(
        string="Has gynecological", compute="_compute_has_gynecological", store=False
    )
    has_non_speculum_gynecological = fields.Boolean(
        string="Has non speculum gynecological",
        compute="_compute_has_non_speculum_gynecological",
        store=False,
    )
    has_post_first_tremester_pregnant = fields.Boolean(
        string="has post first tremester pregnant",
        compute="_compute_has_post_first_tremester_pregnant",
        store=False,
    )
    has_pre_first_tremester_pregnant = fields.Boolean(
        string="Has post first tremester pregnant",
        compute="_compute_has_pre_first_tremester_pregnant",
        store=False,
    )
    has_ultra_sound = fields.Boolean(
        string="Has ultra sound",
        compute="_compute_has_ultra_sound",
        store=False,
    )
    general_result_ids = fields.One2many(
        "z_obstetric.general_result", "visit_id", "General result", copy=True
    )
    has_general_result = fields.Boolean(
        string="Has ultra sound",
        compute="_compute_has_general_result",
        store=False,
    )
    oval_check_idc_ids = fields.One2many(
        "z_obstetric.oval_check_idc",
        "visit_id",
        "Ovalution Checking Indicated",
        copy=True,
    )
    has_oval_check_idc = fields.Boolean(
        string="Has Ovalution Checking Indicated",
        compute="_compute_has_oval_check_idc",
        store=False,
    )

    format_obs_examination_code = fields.Char(
        "Format Obsteric Examination Code",
        compute="_compute_format_obs_examination_code",
    )

    gyn_ult_ids = fields.One2many(
        "z_obstetric.gyn_ult",
        "visit_id",
        "Gynecological ultrasound",
        copy=True,
    )

    full_body_ids = fields.One2many(
        "z_obstetric.full_body", "visit_id", "Full body examination", copy=True
    )

    has_gyn_ult = fields.Boolean(
        string="Has gynecological ultrasound",
        compute="_compute_has_gyn_ult",
        store=False,
    )
    post_first_indicated_ids = fields.One2many(
        "z_obstetric.post_first_indicated",
        "visit_id",
        "Post first indicated",
        copy=True,
    )
    has_post_first_indicated = fields.Boolean(
        string="Has post first indicated",
        compute="_compute_has_post_first_indicated",
        store=False,
    )
    pre_first_indicated_ids = fields.One2many(
        "z_obstetric.pre_first_indicated", "visit_id", "Pre first indicated", copy=True
    )
    has_pre_first_indicated = fields.Boolean(
        string="Has pre first indicated",
        compute="_compute_has_pre_first_indicated",
        store=False,
    )
    fetal_ultrasound_4d_ids = fields.One2many(
        "z_obstetric.fetal_ultrasound", "visit_id", "4D fetal ultrasound", copy=True
    )
    has_fetal_ultrasound_4d = fields.Boolean(
        string="Has 4D fetal ultrasound",
        compute="_compute_has_fetal_ultrasound_4d",
    )
    pdf_title = fields.Char(string="Pdf title", compute="_compute_pdf_title")

    include_ovulation_indicated = fields.Boolean(
        "Include Ovulation Indicated", default=False, tracking=True
    )
    include_pre_first_indicated = fields.Boolean(
        "Include Pre First Indicated", default=False, tracking=True
    )
    include_post_first_indicated = fields.Boolean(
        "Include Post First Indicated", default=False, tracking=True
    )
    include_gynecological_indicated = fields.Boolean(
        "Include Gynecological Indicated", default=False, tracking=True
    )
    include_fetal_ultrasound_4d = fields.Boolean(
        "Include 4D fetal ultrasound", default=False, tracking=True
    )
    include_gynecological_form = fields.Boolean(
        "Include Gynecological Form", default=False, tracking=True
    )
    include_non_speculum_gynecological_form = fields.Boolean(
        "Include Non Speculum Gynecological Form", default=False, tracking=True
    )
    include_pre_first_trimester_pregnant_form = fields.Boolean(
        "Include Pre First Trimester Pregnant Form", default=False, tracking=True
    )
    include_post_first_trimester_pregnant_form = fields.Boolean(
        "Include Post First Trimester Pregnant Form", default=False, tracking=True
    )
    include_full_body_examination_form = fields.Boolean(
        "Include Full Body Examination Form", default=False, tracking=True
    )

    medical_test_line_ids = fields.One2many(
        "z_obstetric.medical_test_line",
        "visit_id",
        string="Services in test",
        copy=True,
        tracking=True
    )
    medical_tips_line_ids = fields.One2many(
        "z_obstetric.medical_tips_line",
        "visit_id",
        string="Services in tips",
        copy=True,
        tracking=True,
    )
    reexamination_date_format = fields.Char(
        compute="_compute_reexamination_date_format"
    )
    examination_note = fields.Char(string="Examination note", size=200)
    booking_date_format = fields.Char(compute="_compute_booking_date_format")
    test_state = fields.Boolean("Test State", compute="_compute_test_state", store=True)
    test_state_selection = fields.Selection(
        [("have_result", "Have result"), ("no_result", "No result")],
        string="Test State",
        default="no_result",
        compute="_compute_test_state",
        store=True,
    )
    z_customer_code = fields.Char(
        "Mã khách hàng", related="customer_id.code", store=True
    )
    date_assign = fields.Date(string="Date assign medical tips", tracking=True)
    date_assign_ddmmyyyy = fields.Char(
        string="Date Assign",
        compute="_compute_date_assign_ddmmyyyy",
    )
    doctor_id = fields.Many2one(tracking=False)
    time_slot_id = fields.Many2one(tracking=False)
    type = fields.Selection(tracking=False)
    booking_type = fields.Selection(tracking=False)
    overbook = fields.Boolean(tracking=False)
    printing_type = fields.Selection(tracking=False)
    date_assign_day = fields.Char(string="Day", compute="_compute_date_parts")
    date_assign_month = fields.Char(string="Month", compute="_compute_date_parts")
    date_assign_year = fields.Char(string="Year", compute="_compute_date_parts")
    state = fields.Selection(
        [
            ("1", "Not yet arrived"),
            ("2", "Waiting"),
            ("3", "Examining"),
            ("4", "Waiting for ultrasound"),
            ("5", "Result SA"),
            ("6", "Result test"),
            ("7", "Waiting for conclude"),
            ("8", "Concluded and register tip"),
            ("9", "Finished"),
            ("10", "Waiting for tip"),
            ("11", "Doing tip"),
            ("12", "Finished tip"),
        ],
        default=AppointmentState.NOT_YET_ARRIVED,
        tracking=False
    )
    technician_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Technician",
        domain="[('bookable','=', True)]",
        tracking=True,
    )
    approach_channel = fields.Selection(
        [
            ("1", "Ads"),
            ("2", "No ads"),
        ],
        default="1",
        string="Approach channel",
    )

    @api.depends(
        "medical_test_line_ids.service_id.name", "medical_test_line_ids.has_result"
    )
    def _compute_test_state(self):
        for record in self:
            record.test_state = False
            record.test_state_selection = "no_result"
            if any(line.has_result
                and (line.service_id.categ_id.categ_code == '05' or line.service_id.categ_id.categ_code == 'KQ')
                for line in record.medical_test_line_ids
            ):
                record.doctor_id.user_id.notify_info(
                    message=f"Trạng thái xét nghiệm của lượt khám {record.examination_code} đã được cập nhật!"
                )
                record.technician_id.user_id.notify_info(
                    message=f"Trạng thái xét nghiệm của lượt khám {record.examination_code} đã được cập nhật!"
                )
                record.create_uid.notify_info(
                    message=f"Trạng thái xét nghiệm của lượt khám {record.examination_code} đã được cập nhật!"
                )
                record.test_state = True
                record.test_state_selection = "have_result"

    @api.depends("customer_id")
    def _compute_pdf_title(self):
        for record in self:
            name = unidecode(record.customer_id.name).replace(" ", "")
            title = _("CLS Specified")
            record.pdf_title = f"{title}_{name}_{record.customer_id.code}"

    @api.depends("pre_first_indicated_ids")
    def _compute_has_pre_first_indicated(self):
        for rec in self:
            rec.has_pre_first_indicated = len(rec.pre_first_indicated_ids) > 0

    @api.depends("post_first_indicated_ids")
    def _compute_has_post_first_indicated(self):
        for rec in self:
            rec.has_post_first_indicated = len(rec.post_first_indicated_ids) > 0

    @api.depends("gyn_ult_ids")
    def _compute_has_gyn_ult(self):
        for rec in self:
            rec.has_gyn_ult = len(rec.gyn_ult_ids) > 0

    @api.depends("fetal_ultrasound_4d_ids")
    def _compute_has_fetal_ultrasound_4d(self):
        for rec in self:
            rec.has_fetal_ultrasound_4d = len(rec.fetal_ultrasound_4d_ids) > 0

    @api.depends("general_result_ids")
    def _compute_has_general_result(self):
        for rec in self:
            rec.has_general_result = len(rec.general_result_ids) > 0

    @api.depends("gynecological_ids")
    def _compute_has_gynecological(self):
        for rec in self:
            rec.has_gynecological = len(rec.gynecological_ids) > 0

    @api.depends("non_speculum_gynecological_ids")
    def _compute_has_non_speculum_gynecological(self):
        for rec in self:
            rec.has_non_speculum_gynecological = (
                len(rec.non_speculum_gynecological_ids) > 0
            )

    @api.depends("pre_first_tremester_pregnant_ids")
    def _compute_has_pre_first_tremester_pregnant(self):
        for rec in self:
            rec.has_pre_first_tremester_pregnant = (
                len(rec.pre_first_tremester_pregnant_ids) > 0
            )

    @api.depends("post_first_tremester_pregnant_ids")
    def _compute_has_post_first_tremester_pregnant(self):
        for rec in self:
            rec.has_post_first_tremester_pregnant = (
                len(rec.post_first_tremester_pregnant_ids) > 0
            )

    @api.depends("ultra_sound_ids")
    def _compute_has_ultra_sound(self):
        for rec in self:
            rec.has_ultra_sound = len(rec.ultra_sound_ids) > 0

    @api.depends("oval_check_idc_ids")
    def _compute_has_oval_check_idc(self):
        for rec in self:
            rec.has_oval_check_idc = len(rec.oval_check_idc_ids) > 0

    @api.depends("general_result_ids.reexamination_date")
    def _compute_reexamination_date_format(self):
        for record in self:
            if (
                record.general_result_ids
                and record.general_result_ids[0].reexamination_date
            ):
                reexamination_date = record.general_result_ids[0].reexamination_date
                record.reexamination_date_format = datetime.strptime(
                    str(reexamination_date), "%Y-%m-%d"
                ).strftime("%d/%m/%Y")
            else:
                record.reexamination_date_format = ""

    @api.depends("booking_date")
    def _compute_booking_date_format(self):
        for record in self:
            if record.booking_date:
                booking_date = record.booking_date
                record.booking_date_format = datetime.strptime(
                    str(booking_date), "%Y-%m-%d"
                ).strftime("Ngày %d tháng %m năm %Y")
            else:
                record.booking_date_format = ""

    def action_open_medical_result_form(
        self,
        res_model: str,
        name: str,
        examination_type: str,
        code: str,
        is_pop_up=True,
    ):
        target = "new" if is_pop_up else "current"
        medical = self.env[res_model].search([("visit_id", "=", self.id)], limit=1)
        if medical:
            return {
                "type": "ir.actions.act_window",
                "name": name,
                "view_mode": "form",
                "res_model": res_model,
                "res_id": medical.id,
                "context": {},
                "target": target,
            }
        else:
            return {
                "type": "ir.actions.act_window",
                "name": name,
                "view_mode": "form",
                "res_model": res_model,
                "res_id": None,
                "context": {
                    "default_visit_id": self.id,
                    "default_customer_id": self.customer_id.id,
                    "default_optometrist_id": self.technician_id.id,
                    "default_examiner_id": self.doctor_id.id,
                    "default_examination_date": self.time_slot_start_time.date(),
                    "default_code": code,
                    "default_examination_type": examination_type,
                },
                "target": target,
            }

    def action_open_post_first_trimester_pregnant_form(self):
        res_model = "z_obstetric.post_pregnant"
        name = _("Post-First Tremester Pregnant")
        examination_type = _("Post-First Tremester Pregnant")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "KLS"
        )

    def action_open_full_body_examination_form(self):
        res_model = "z_obstetric.full_body"
        name = _("Full body examination")
        examination_type = _("Full body examination")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "KLS"
        )

    def action_open_pre_first_trimester_pregnant_form(self):
        res_model = "z_obstetric.pre_pregnant"
        name = _("Pre-First Tremester Pregnant")
        examination_type = _("Pre-First Tremester Pregnant")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "KLS"
        )

    def action_open_gynecological_form(self):
        res_model = "z_obstetric.gynecological"
        name = _("Gynecological")
        examination_type = _("Gynecological")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "KLS"
        )

    def action_open_non_speculum_gynecological_form(self):
        res_model = "z_obstetric.non_gynecological"
        name = _("Non Speculum Gynecological")
        examination_type = _("Non Speculum Gynecological")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "KLS"
        )

    def action_open_ultra_sound_form(self):
        res_model = "z_obstetric.ultra_sound"
        name = _("Ultra sound")
        examination_type = _("Ultra sound")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "XN"
        )

    def action_open_general_result_form(self):
        res_model = "z_obstetric.general_result"
        name = _("General result")
        examination_type = _("General result")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "XN", False
        )

    def action_open_gyn_ult_form(self):
        res_model = "z_obstetric.gyn_ult"
        name = _("Gynecological ultrasound")
        examination_type = _("Gynecological ultrasound")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "XN"
        )

    def action_open_post_first_indicated_form(self):
        res_model = "z_obstetric.post_first_indicated"
        name = _("Post first indicated")
        examination_type = _("Post first indicated")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "XN"
        )

    def action_open_pre_first_indicated_form(self):
        res_model = "z_obstetric.pre_first_indicated"
        name = _("Pre first indicated")
        examination_type = _("Pre first indicated")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "XN"
        )

    def action_open_ovalution_indcated(self):
        res_model = "z_obstetric.oval_check_idc"
        name = _("Ovalution Checking Indicated")
        examination_type = _("Ovalution Checking Indicated")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "XN"
        )

    def action_open_test_form(self):
        res_model = "z_obstetric.medical_test"
        name = _("Ovalution Checking Indicated")
        examination_type = _("Ovalution Checking Indicated")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "TT", False
        )

    def action_open_examination_form(self):
        res_model = "z_appointment.appointment"
        return {
            "type": "ir.actions.act_window",
            "name": "Examination",
            "view_mode": "form",
            "res_model": res_model,
            "res_id": self.id,
            "target": "current",
            "views": [
                (
                    self.env.ref("z_obstetric.z_obstetric_examination_form_view").id,
                    "form",
                )
            ],
        }

    def action_open_indicated_form(self):
        res_model = "z_appointment.appointment"
        return {
            "type": "ir.actions.act_window",
            "name": "Indicated",
            "view_mode": "form",
            "res_model": res_model,
            "res_id": self.id,
            "target": "current",
            "views": [
                (self.env.ref("z_obstetric.z_obstetric_indicated_form_view").id, "form")
            ],
        }

    def action_open_tips_form(self):
        res_model = "z_appointment.appointment"
        return {
            "type": "ir.actions.act_window",
            "name": "Tips",
            "view_mode": "form",
            "res_model": res_model,
            "res_id": self.id,
            "target": "current",
            "views": [
                (self.env.ref("z_obstetric.z_obstetric_tips_form_view").id, "form")
            ],
        }

    def action_open_sentence_form(self):
        action = self.env["ir.actions.report"]._for_xml_id(
            "z_obstetric.action_report_conclude_result"
        )
        return action

    def action_open_fetal_ultrasound_4d(self):
        res_model = "z_obstetric.fetal_ultrasound"
        name = _("4D fetal ultrasound")
        examination_type = _("4D fetal ultrasound")
        return self.action_open_medical_result_form(
            res_model, name, examination_type, "XN"
        )

    def action_print(self):
        pass

    def check_fields_exist(self, titleOn, fields):
        self.ensure_one()
        if titleOn and eval(f"self.{titleOn}"):
            for field in fields:
                field_value = eval(f"self.{field}")
                if field_value:
                    return True
        return False

    @api.depends("examination_code")
    def _compute_format_obs_examination_code(self):
        for rec in self:
            format_obs_examination_code = False
            if rec.examination_code:
                year_month_day = rec.examination_code[2:8]
                last_four_digits = rec.examination_code[8:]
                format_obs_examination_code = f"/{year_month_day}/{last_four_digits}"
            rec.format_obs_examination_code = format_obs_examination_code

    # check khám phụ khoa (Khám lâm sàng)
    def check_conditions_gynecological_examination(self):
        titleOn = "include_gynecological_form"
        fields = [
            "gynecological_ids.ah",
            "gynecological_ids.ad",
            "gynecological_ids.tc",
            "gynecological_ids.ctc",
            "gynecological_ids.two_pp",
            "gynecological_ids.other",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check khám phụ khoa không mỏ vịt (Khám lâm sàng)
    def check_conditions_gynecological_examination_without_speculum(self):
        titleOn = "include_non_speculum_gynecological_form"
        fields = [
            "non_speculum_gynecological_ids.ah",
            "non_speculum_gynecological_ids.hymen",
            "non_speculum_gynecological_ids.ad",
            "non_speculum_gynecological_ids.other",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check khám thai dưới 3 tháng (Khám lâm sàng)
    def check_conditions_pregnant_pre_first_trimester(self):
        titleOn = "include_pre_first_trimester_pregnant_form"
        fields = [
            "pre_first_tremester_pregnant_ids.blood_pressure",
            "pre_first_tremester_pregnant_ids.cardiopulmonary",
            "pre_first_tremester_pregnant_ids.fetal_heart",
            "pre_first_tremester_pregnant_ids.pulse",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check khám thai trên 3 tháng (Khám lâm sàng)
    def check_conditions_pregnant_post_first_trimester(self):
        titleOn = "include_post_first_trimester_pregnant_form"
        fields = [
            "post_first_tremester_pregnant_ids.blood_pressure",
            "post_first_tremester_pregnant_ids.pulse",
            "post_first_tremester_pregnant_ids.cardiopulmonary",
            "post_first_tremester_pregnant_ids.edema",
            "post_first_tremester_pregnant_ids.cervical_length",
            "post_first_tremester_pregnant_ids.fetal_position",
            "post_first_tremester_pregnant_ids.fetal_heart",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check khám toàn thân (Khám lâm sàng)
    def check_conditions_full_body(self):
        titleOn = "include_full_body_examination_form"
        fields = [
            "full_body_ids.perception",
            "full_body_ids.blood_pressure",
            "full_body_ids.physical_condition",
            "full_body_ids.skin_mucous_membrane",
        ]
        return self.check_fields_exist(titleOn, fields)

    # Các xét nghiệm và thăm dò chính
    # check chuẩn đoán - kết quả theo dõi nang noãn
    def check_conditions_diagnostic(self):
        titleOn = "include_ovulation_indicated"
        fields = [
            "oval_check_idc_ids.menstrual",
            "oval_check_idc_ids.menstrual_cycle",
            "oval_check_idc_ids.kcc",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check tử cung - kết quả theo dõi nang noãn
    def check_conditions_ulterus(self):
        titleOn = "include_ovulation_indicated"
        fields = [
            "oval_check_idc_ids.position",
            "oval_check_idc_ids.size",
            "oval_check_idc_ids.other_image",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check theo dõi nang noãn - kết quả theo dõi nang noãn
    def check_conditions_follicle_monitoring(self):
        return (
            self.include_ovulation_indicated
            and len(self.oval_check_idc_ids.cheking_ids) > 0
        )

    # check kcc - siêu âm thai dưới 3 tháng
    def check_conditions_kcc_after(self):
        titleOn = "include_pre_first_indicated"
        fields = [
            "pre_first_indicated_ids.kcc",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check tuổi thai - siêu âm thai dưới 3 tháng
    def check_conditions_pregnant_age_after(self):
        titleOn = "include_pre_first_indicated"
        fields = [
            "pre_first_indicated_ids.pregnant_age_1",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check thai - siêu âm thai dưới 3 tháng
    def check_conditions_pregnancy(self):
        titleOn = "include_pre_first_indicated"
        fields = [
            "pre_first_indicated_ids.quantity_fetal",
            "pre_first_indicated_ids.position_fetal",
            "pre_first_indicated_ids.amniotic_sac",
            "pre_first_indicated_ids.heart_fetal",
            "pre_first_indicated_ids.length",
            "pre_first_indicated_ids.biparietal",
            "pre_first_indicated_ids.gesture",
            "pre_first_indicated_ids.light_neck_back",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check hình ảnh khác - siêu âm thai dưới 3 tháng
    def check_conditions_other_image_pre(self):
        titleOn = "include_pre_first_indicated"
        fields = [
            "pre_first_indicated_ids.other_image",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check dự kiến sinh - siêu âm thai dưới 3 tháng
    def check_conditions_expected_date(self):
        titleOn = "include_pre_first_indicated"
        fields = [
            "pre_first_indicated_ids.expected_birth",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check tuổi thai - siêu âm thai dưới 3 tháng
    def check_conditions_pregnant_age(self):
        titleOn = "include_pre_first_indicated"
        fields = [
            "pre_first_indicated_ids.pregnant_age_2",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check thai - siêu âm thai trên 3 tháng
    def check_conditions_pregnant(self):
        titleOn = "include_post_first_indicated"
        fields = [
            "post_first_indicated_ids.quantity_fetal",
            "post_first_indicated_ids.position_fetal",
            "post_first_indicated_ids.heart_fetal",
            "post_first_indicated_ids.biparietal",
            "post_first_indicated_ids.femur_length",
            "post_first_indicated_ids.abdominal_circumference",
            "post_first_indicated_ids.weight",
            "post_first_indicated_ids.pregnant_age",
            "post_first_indicated_ids.expected_birth",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check phần phụ thai - siêu âm thai trên 3 tháng
    def check_conditions_conception_part(self):
        titleOn = "include_post_first_indicated"
        fields = [
            "post_first_indicated_ids.amniotic_sac",
            "post_first_indicated_ids.placenta_position",
            "post_first_indicated_ids.placenta",
            "post_first_indicated_ids.maturity_level",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check hình ảnh khác - siêu âm thai trên 3 tháng
    def check_conditions_other_image_post(self):
        titleOn = "include_post_first_indicated"
        fields = [
            "post_first_indicated_ids.other_image",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check tử cung - siêu âm phụ khoa
    def check_conditions_uterus(self):
        titleOn = "include_gynecological_indicated"
        fields = [
            "gyn_ult_ids.position",
            "gyn_ult_ids.size",
            "gyn_ult_ids.structure",
            "gyn_ult_ids.endometrium",
            "gyn_ult_ids.other_image_uterus",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check phần phụ thai - siêu âm phụ khoa
    def check_conditions_extra(self):
        titleOn = "include_gynecological_indicated"
        fields = [
            "gyn_ult_ids.right_ovary",
            "gyn_ult_ids.left_ovary",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check douglas - siêu âm phụ khoa
    def check_conditions_douglas(self):
        titleOn = "include_gynecological_indicated"
        fields = ["gyn_ult_ids.douglas"]
        return self.check_fields_exist(titleOn, fields)

    # check hình ảnh khác - siêu âm phụ khoa
    def check_conditions_other_image_gyn_ult(self):
        fields = ["gyn_ult_ids.other_image"]
        return self.check_fields_exist(False, fields)

    # check thai - siêu âm thai 4D
    def check_conditions_fetal_fetal_ultrasound(self):
        titleOn = "include_fetal_ultrasound_4d"
        fields = [
            "fetal_ultrasound_4d_ids.quantity_fetal",
            "fetal_ultrasound_4d_ids.edge_of_skull",
            "fetal_ultrasound_4d_ids.head_circumference",
            "fetal_ultrasound_4d_ids.nasal_spine",
            "fetal_ultrasound_4d_ids.anterior_abdominal_wall",
            "fetal_ultrasound_4d_ids.stomach_image",
            "fetal_ultrasound_4d_ids.spine",
            "fetal_ultrasound_4d_ids.femur_length",
            "fetal_ultrasound_4d_ids.limb_posture",
            "fetal_ultrasound_4d_ids.amniotic_status",
            "fetal_ultrasound_4d_ids.head_butt_length",
            "fetal_ultrasound_4d_ids.fetal_weight",
            "fetal_ultrasound_4d_ids.fetal_movement",
            "fetal_ultrasound_4d_ids.diagonal_diameter",
            "fetal_ultrasound_4d_ids.midline_structure",
            "fetal_ultrasound_4d_ids.fetal_heart_rate",
            "fetal_ultrasound_4d_ids.abdominal_circumference",
            "fetal_ultrasound_4d_ids.bladder",
            "fetal_ultrasound_4d_ids.limbs",
            "fetal_ultrasound_4d_ids.foot_length",
            "fetal_ultrasound_4d_ids.placenta_position",
            "fetal_ultrasound_4d_ids.umbilical_cord",
            "fetal_ultrasound_4d_ids.light_neck_back",
            "fetal_ultrasound_4d_ids.expected_birth",
        ]
        return self.check_fields_exist(titleOn, fields)

    # check hình ảnh khác - siêu âm thai 4D
    def check_conditions_other_image_fetal_ultrasound(self):
        fields = ["fetal_ultrasound_4d_ids.other_image"]
        return self.check_fields_exist(False, fields)

    # check chẩn đoán - siêu âm thai 4D
    def check_conditions_diagnose_fetal_ultrasound(self):
        titleOn = "include_fetal_ultrasound_4d"
        fields = [
            "fetal_ultrasound_4d_ids.diagnose",
        ]
        return self.check_fields_exist(titleOn, fields)
    
    # check lưu ý - siêu âm thai 4D
    def check_conditions_note_fetal_ultrasound(self):
        titleOn = "include_fetal_ultrasound_4d"
        fields = [
            "fetal_ultrasound_4d_ids.diagnose",
        ]
        return self.check_fields_exist(titleOn, fields)
    
    # check danh sách chỉ định và xét nghiệm
    def check_conditions_laboratory_test_order(self):
        return len(self.medical_test_line_ids) > 0

    def check_title_examination(self):
        return (
            self.check_conditions_gynecological_examination()
            or self.check_conditions_gynecological_examination_without_speculum()
            or self.check_conditions_pregnant_pre_first_trimester()
            or self.check_conditions_pregnant_post_first_trimester()
            or self.check_conditions_full_body()
        )

    def check_title_ovarian_follicle_result(self):
        return self.include_ovulation_indicated and (
            self.check_conditions_diagnostic()
            or self.check_conditions_ulterus()
            or self.check_conditions_follicle_monitoring()
        )

    def check_title_pregnant_pre_first(self):
        return self.include_pre_first_indicated and (
            self.check_conditions_kcc_after()
            or self.check_conditions_pregnant_age_after()
            or self.check_conditions_pregnancy()
            or self.check_conditions_other_image_pre()
            or self.check_conditions_expected_date()
            or self.check_conditions_pregnant_age()
        )

    def check_title_pregnant_post_first(self):
        return self.include_post_first_indicated and (
            self.check_conditions_pregnant()
            or self.check_conditions_conception_part()
            or self.check_conditions_other_image_post()
        )

    def check_title_gynecological_ultrasound_results(self):
        return self.include_gynecological_indicated and (
            self.check_conditions_uterus()
            or self.check_conditions_extra()
            or self.check_conditions_douglas()
            or self.check_conditions_other_image_gyn_ult()
        )
    
    def check_title_fetal_ultrasound_results(self):
        return self.include_fetal_ultrasound_4d and (
            self.check_conditions_fetal_fetal_ultrasound()
            or self.check_conditions_other_image_fetal_ultrasound()
            or self.check_conditions_diagnose_fetal_ultrasound()
            or self.check_conditions_note_fetal_ultrasound()
        )

    def check_title_test_and_investigations(self):
        return (
            self.check_title_ovarian_follicle_result()
            or self.check_title_pregnant_pre_first()
            or self.check_title_pregnant_post_first()
            or self.check_title_gynecological_ultrasound_results()
            or self.check_conditions_laboratory_test_order()
            or self.check_title_fetal_ultrasound_results()
        )

    def action_create_invoices_drug(self):
        if int(self.state) == 1:
            raise ValidationError("Trạng thái 'Chưa đến' không thể tạo hoá đơn'")
        return {
            "type": "ir.actions.act_window",
            "name": "Thanh toán",
            "view_mode": "form",
            "res_model": "account.move",
            "view_id": self.env.ref("z_obstetric.z_invoice_form_view_drug_inherit").id,
            "res_id": None,
            "id": self.env.ref("z_obstetric.z_invoice_obs_for_drug_order").id,
            "context": {
                "default_partner_id": self.customer_id.id,
                "default_partner_dob": self.customer_id.date,
                "default_partner_address": self.customer_id.street,
                "default_partner_job": self.customer_id.job,
                "default_move_type": "out_invoice",
                "default_z_appointment_id": self.id,
                "default_company_id": self.env.company.id,
                "linked_from_appointment": True,
                "drug_order": True,
            },
            "target": "current",
        }

    def action_create_invoices(self):
        if int(self.state) == 1:
            raise ValidationError("Trạng thái 'Chưa đến' không thể tạo hoá đơn'")
        return {
            "type": "ir.actions.act_window",
            "name": "Thanh toán",
            "view_mode": "form",
            "view_id": self.env.ref(
                "z_obstetric.z_invoice_form_view_service_inherit"
            ).id,
            "res_model": "account.move",
            "res_id": None,
            "id": self.env.ref("z_obstetric.z_invoice_obs_for_service_order").id,
            "context": {
                "default_partner_id": self.customer_id.id,
                "default_partner_dob": self.customer_id.date,
                "default_partner_address": self.customer_id.street,
                "default_partner_job": self.customer_id.job,
                "default_move_type": "out_invoice",
                "default_z_appointment_id": self.id,
                "default_company_id": self.env.company.id,
                "linked_from_appointment": True,
                "drug_order": False,
            },
            "target": "current",
        }

    @api.depends("date_assign")
    def _compute_date_assign_ddmmyyyy(self):
        for record in self:
            record.date_assign_ddmmyyyy = (
                record.date_assign.strftime("%d/%m/%Y") if record.date_assign else False
            )

    @api.depends('booking_date')
    def _compute_date_parts(self):
        for record in self:
            record.date_assign_day = str(record.booking_date.day).zfill(2) if record.booking_date else " ... "
            record.date_assign_month = str(record.booking_date.month).zfill(2) if record.booking_date else " ... "
            record.date_assign_year = str(record.booking_date.year) if record.booking_date else " ... "
            
    def write(self, vals):
        if vals.get("state") == "1" and (
            self.has_gynecological
            or self.has_non_speculum_gynecological
            or self.has_post_first_tremester_pregnant
            or self.has_pre_first_tremester_pregnant
            or self.has_ultra_sound
            or self.has_general_result
            or self.has_gyn_ult
            or self.has_oval_check_idc
            or self.has_pre_first_indicated
            or self.has_post_first_indicated
            or self.has_fetal_ultrasound_4d
            or self.has_invoice
        ):
            raise ValidationError(
                _("It is not possible to update the unarrived status for a visit that has already arrived")
            )
        return super().write(vals)
