from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class FootballContract(models.Model):
    _name = 'football.contract'
    _description = 'Football Contract'

    player_id = fields.Many2one(
        'football.player',
        required=True
    )

    team_id = fields.Many2one(
        related='player_id.team_id',
        store=True
    )

    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    salary = fields.Float(required=True)

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired')
    ], compute="_compute_state", store=True)

    @api.depends('date_end')
    def _compute_state(self):
        today = date.today()
        for rec in self:
            rec.state = (
                'expired'
                if rec.date_end and rec.date_end < today
                else 'active'
            )