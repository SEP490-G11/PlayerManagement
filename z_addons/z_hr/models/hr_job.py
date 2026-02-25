# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.z_web.helpers.utils import ZUtils

import re, json


class ZHrJob(models.Model):
    _inherit = ["hr.job"]

    acronym = fields.Char(string="Acronym", required=True)
    bookable = fields.Boolean("Bookable", default=False, tracking=True)
    is_doctor = fields.Boolean("Is doctor", default=False, tracking=True)
    deletable = fields.Boolean("Can delete", default=True)

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            if rec.deletable and len(rec.name) > 128:
                raise ValidationError(
                    _("Job name must consist of up to 128.")
                )
            if rec.deletable and len(self.search([("name", "=ilike", rec.name)])) > 1:
                raise ValidationError(_("Job position name is must be unique"))
            if len(rec.name.strip()) == 0:
                raise ValidationError(_("Job position can not empty"))
            
    @api.constrains("acronym")
    def _check_acroym(self):
        for rec in self:
            if rec.deletable and rec.acronym and len(self.search([("acronym", "=ilike", rec.acronym)])) > 1:
                raise ValidationError(_("Job position acronym is must be unique"))
            if rec.deletable and rec.acronym and len(rec.acronym) > 15:
                raise ValidationError(
                    _("Acronym must consist of up to 15.")
                )
            if len(rec.acronym.strip()) == 0:
                raise ValidationError(_("Acronym can not empty"))

    def unlink(self):
        for rec in self:
            employee = self.env['hr.employee'].search([("job_id", "=", rec.id)], limit=1)
            if employee:
                raise ValidationError(_("Have a employee which assigned to this job"))
            if not rec.deletable: 
                raise ValidationError(_("This job can't be delete"))
            else:
               return super().unlink()
            
    def write(self, vals):
            if not self.deletable:
                raise ValidationError(_("This job can't be edit"))
            vals = {k: v.strip() if isinstance(v, str) else v for k, v in vals.items()}
            return super(ZHrJob, self).write(vals)

    @api.model
    def create(self, vals):
        vals = {k: v.strip() if isinstance(v, str) else v for k, v in vals.items()}
        return super(ZHrJob, self).create(vals)
