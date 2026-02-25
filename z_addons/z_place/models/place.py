# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.z_web.helpers.model_utils import ZModelUtils
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_place.helpers.constants import PlaceErrorCode
import re


class ZPlace(models.Model):
    _name = "z_place.place"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Place"

    name = fields.Char("Name", required=True, tracking=True)
    active = fields.Boolean(string="Active", default=True)
    address = fields.Text(string="Address")
    
    
    z_system_payos_client_id = fields.Char(
        string="PayOS Client ID",
        config_parameter="z_payos.z_system_payos_client_id"
    )

    z_system_payos_api_key = fields.Char(
        string="PayOS API Key",
    )

    z_system_payos_checksum_key = fields.Char(
        string="PayOS Checksum Key",
    )
    
    z_system_payos_return_url = fields.Char(
        string="PayOS Return URL",
        config_parameter="z_payos.z_system_payos_return_url"
    )

    z_system_payos_cancel_url = fields.Char(
        string="PayOS Cancel URL",
        config_parameter="z_payos.z_system_payos_cancel_url"
    )

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            if rec.name and len(rec.name) > 128:
                raise ValidationError(_("Place name must be smaller than 128."))
            if len(self.search([("name", "=ilike", rec.name)])) > 1:
                raise ValidationError(_("Place name is must be unique"))
            if len(rec.name.strip()) == 0:
                raise ValidationError(_("Place name can not empty"))

    def get_place_by_id(self, employee_id):
        return ZModelUtils.get_record_by_id(
            self, employee_id, PlaceErrorCode.PLACE_DOES_NOT_EXIST
        )

    def write(self, values):
        for rec in self:
            if "active" in values and values["active"] == False:
                timeslot = self.env["z_hr.time_slot"].search(
                    [
                        ("booked", "=", True),
                        ("place_id", "=", rec.id),
                        ("start_time", ">=", ZUtils.now()),
                    ],
                    limit=1,
                )
                if timeslot:
                    raise ValidationError(
                        _("You cannot archive a place that has appointments in future.")
                    )
                values = {k: v.strip() if isinstance(v, str) else v for k, v in values.items()}
                return super(ZPlace, self).write(values)
            else:
                return super(ZPlace, self).write(values)

    def unlink(self):
        for rec in self:
            employee = self.env["hr.employee"].search([("place_ids", "=", rec.id)])
            timeslot = self.env["z_hr.time_slot"].search(
                [("booked", "=", True), ("place_id", "=", rec.id)], limit=1
            )
            if timeslot:
                raise ValidationError(
                    _("You cannot delete a place that has appointments.")
                )
            if employee:
                raise ValidationError(
                    _("You cannot delete a place that has linked employees.")
                )

        return super(ZPlace, self).unlink()

    @api.model
    def create(self, vals):
        vals = {k: v.strip() if isinstance(v, str) else v for k, v in vals.items()}
        return super(ZPlace, self).create(vals)
