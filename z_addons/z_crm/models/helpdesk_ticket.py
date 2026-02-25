# -*- coding: utf-8 -*-

import ast
from dateutil.relativedelta import relativedelta

from odoo import api, Command, fields, models, tools, _
from odoo.exceptions import AccessError
from odoo.osv import expression
from odoo.addons.web.controllers.utils import clean_action


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # Fields declaration selection for  Chăn sóc đặt lịch, Chăm sóc kính  và Chăn sóc phần mềm
    z_ticket_type = fields.Selection(
        [
            ("ab", _("Appointment Booking")),
            ("gotc", _("Glass Order Take Care")),
            ("sm", _("Software Maintenance")),
        ],
        string="Ticket Type",
    )

    deadline_task = fields.Date(
        string="Deadline Task", compute="_compute_deadline_task", store=True
    )
    execute_date = fields.Date(
        "Execute Date", compute="_compute_execute_date", store=True
    )

    # Hàm tính ra deadline task theo thời gian được tạo ticket là cuối ngày
    @api.depends("create_date")
    def _compute_deadline_task(self):
        for record in self:
            if record.create_date:
                record.deadline_task = record.create_date + relativedelta(days=1)
            else:
                record.deadline_task = False

    @api.depends("sla_deadline")
    def _compute_execute_date(self):
        for rec in self:
            rec.execute_date = rec.sla_deadline.date() if rec.sla_deadline else False
