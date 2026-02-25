# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta


class ZGlassOrderSequence(models.Model):
    _name = "z.glass.order.sequence"
    _description = "Glass Order Sequence"

    name = fields.Char(string="Glass Order Sequence")

    @api.model
    def delete_old_records(self):
        old_records = self.search([("create_date", "<", datetime.now())])
        old_records.unlink()
