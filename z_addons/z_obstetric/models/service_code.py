# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ZServiceCode(models.Model):
    _name = "service.code"
    _description = "Service Code"

    name = fields.Char("Service Name")
    service_name = fields.Char("Code")

    @api.depends("service_name")
    def _compute_display_name(self):
        for rec in self:
            if rec.service_name:
                rec.display_name = "%s" % rec.service_name

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        if name:
            args += [
                "|",
                ("name", operator, name),
                ("service_name", operator, name),
            ]
        fields = self.search(args, limit=limit)
        return fields.name_get()
