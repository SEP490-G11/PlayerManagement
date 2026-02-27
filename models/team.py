from odoo import models, fields, api


class Team(models.Model):
    _name = 'football.team'
    _description = 'Football Team'
    _order = "points desc, goal_difference desc, goals_for desc"

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

    # =========================
    # Financial Info
    # =========================

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

    # =========================
    # League Table Statistics
    # =========================

    played = fields.Integer(compute="_compute_stats")
    won = fields.Integer(compute="_compute_stats")
    draw = fields.Integer(compute="_compute_stats")
    lost = fields.Integer(compute="_compute_stats")
    goals_for = fields.Integer(compute="_compute_stats", store=True)
    goals_against = fields.Integer(compute="_compute_stats")
    goal_difference = fields.Integer(compute="_compute_stats", store=True)
    points = fields.Integer(compute="_compute_stats", store=True)

    def _get_current_season(self):
        today = fields.Datetime.now()
        return self.env['football.season'].search([
            ('start_date', '<=', today),
            ('end_date', '>=', today)
        ], limit=1)

    def _compute_stats(self):
        season = self._get_current_season()

        for team in self:
            if not season:
                team.played = 0
                team.won = 0
                team.draw = 0
                team.lost = 0
                team.goals_for = 0
                team.goals_against = 0
                team.goal_difference = 0
                team.points = 0
                continue

            matches = self.env['football.match'].search([
                ('season_id', '=', season.id),
                ('state', '=', 'played'),
                '|',
                ('home_team_id', '=', team.id),
                ('away_team_id', '=', team.id),
            ])

            played = won = draw = lost = 0
            gf_total = ga_total = 0

            for match in matches:

                if match.home_team_id == team:
                    gf = match.home_score or 0
                    ga = match.away_score or 0
                else:
                    gf = match.away_score or 0
                    ga = match.home_score or 0

                played += 1
                gf_total += gf
                ga_total += ga

                if gf > ga:
                    won += 1
                elif gf == ga:
                    draw += 1
                else:
                    lost += 1

            team.played = played
            team.won = won
            team.draw = draw
            team.lost = lost
            team.goals_for = gf_total
            team.goals_against = ga_total
            team.goal_difference = gf_total - ga_total
            team.points = won * 3 + draw