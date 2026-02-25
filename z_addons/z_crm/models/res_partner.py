# -*- coding: utf-8 -*-
import re
from datetime import date
from typing import Dict, List
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.z_partner.helpers.constants import (
    PartnerErrorCode,
    CUSTOMER_RECORD_LIMIT,
)
from odoo.addons.z_web.helpers.model_utils import ZModelUtils
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_web.helpers.validation import ZValidation


class ZPartner(models.Model):
    _inherit = "res.partner"

    zns_template_ids = fields.Many2many(
        comodel_name="z.crm.zns.template.queue",
        string="ZNS Templates",
        compute="_compute_zns_template_ids",
    )
    task_template_ids = fields.Many2many(
        comodel_name="z.crm.task.template.queue",
        string="Task Templates",
        compute="_compute_task_template_ids",
    )

    # i want to compute task_template_ids by query all z.crm.queue.template.queue with partner_id = self.id and type = 'task' and crm_queue_id not False
    # but i don't know how to do it, so i use this method to compute task_template_ids
    @api.depends()
    def _compute_task_template_ids(self):
        for record in self:
            record.task_template_ids = self.env["z.crm.task.template.queue"].search(
                [
                    ("partner_id", "=", record.id),
                    ("method", "=", "task"),
                    ("crm_queue_id", "!=", False),
                ]
            )

    @api.depends()
    def _compute_zns_template_ids(self):
        for record in self:

            record.zns_template_ids = self.env["z.crm.zns.template.queue"].search(
                [
                    ("partner_id", "=", record.id),
                    ("method", "=", "zns"),
                    ("crm_queue_id", "!=", False),
                ]
            )
