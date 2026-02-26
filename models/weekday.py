from odoo import models, fields

class FootballWeekday(models.Model):
    _name = 'football.weekday'
    _description = 'Weekday'

    name = fields.Char(required=True)
    code = fields.Integer(required=True)  # 0=Monday ... 6=Sunday