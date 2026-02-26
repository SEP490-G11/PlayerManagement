from odoo import models, fields, api

class Team(models.Model):
    _name = 'football.team'
    _description = 'Football Team'

    name = fields.Char(required=True)
    coach = fields.Char()
    founded_year = fields.Integer()

    player_ids = fields.One2many(
        'football.player',
        'team_id'
    )

    contract_ids = fields.One2many(
        'football.contract',
        'team_id'
    )

    total_market_value = fields.Float(
        compute="_compute_total_value",
        store=True
    )

    total_salary = fields.Float(
        compute="_compute_total_salary",
        store=True
    )

    @api.depends('player_ids.market_value')
    def _compute_total_value(self):
        for team in self:
            team.total_market_value = sum(
                team.player_ids.mapped('market_value')
            )

    @api.depends('contract_ids.salary', 'contract_ids.state')
    def _compute_total_salary(self):
        for team in self:
            active = team.contract_ids.filtered(
                lambda c: c.state == 'active'
            )
            team.total_salary = sum(active.mapped('salary'))