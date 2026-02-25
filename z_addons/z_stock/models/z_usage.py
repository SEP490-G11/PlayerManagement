from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ZUsage(models.Model):
    _name = "z.usage"

    name = fields.Char(string="Name", required=True)
