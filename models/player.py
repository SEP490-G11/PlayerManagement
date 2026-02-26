from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Player(models.Model):
    _name = 'football.player'
    _description = 'Football Player'

    name = fields.Char(required=True)
    age = fields.Integer()
    position = fields.Selection([
        ('gk', 'GK'),
        ('df', 'DF'),
        ('mf', 'MF'),
        ('fw', 'FW')
    ])

    number = fields.Integer()
    nationality = fields.Char()
    market_value = fields.Float()

    team_id = fields.Many2one(
        'football.team',
        required=True
    )

    image = fields.Binary(string="Ảnh cầu thủ")

    @api.constrains('number', 'team_id')
    def _check_unique_number(self):
        for rec in self:
            domain = [
                ('number', '=', rec.number),
                ('team_id', '=', rec.team_id.id),
                ('id', '!=', rec.id)
            ]
            if self.search_count(domain):
                raise ValidationError("Số áo đã tồn tại.")