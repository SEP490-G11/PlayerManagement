from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class FootballSeason(models.Model):
    _name = 'football.season'
    _description = 'Football Season'

    name = fields.Char(required=True)

    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)

    match_duration_hours = fields.Float(default=2.0)

    allowed_weekday_ids = fields.Many2many(
    'football.weekday',
    string="Allowed Weekdays"
)

    match_ids = fields.One2many(
        'football.match',
        'season_id'
    )

    def action_generate_schedule(self):
        self.ensure_one()

        teams = list(self.env['football.team'].search([]))

        if len(teams) != 20:
            raise ValidationError("EPL cần đúng 20 đội.")

        # Double round robin (38 rounds)
        rounds = self._double_round_robin(teams)

        total_weeks = len(rounds)

        season_days = (self.end_date - self.start_date).days
        weeks_available = season_days // 7

        if weeks_available < total_weeks:
            raise ValidationError("Khoảng thời gian không đủ cho 38 vòng.")

        current_date = self.start_date
        duration = timedelta(hours=self.match_duration_hours)

        for round_matches in rounds:
            allowed_days = self.allowed_weekday_ids.mapped('code')
            # Tìm ngày hợp lệ trong tuần
            while current_date.weekday() not in allowed_days:
                current_date += timedelta(days=1)

            slot_time = current_date

            for home, away in round_matches:

                self.env['football.match'].create({
                    'season_id': self.id,
                    'home_team_id': home.id,
                    'away_team_id': away.id,
                    'match_date': slot_time,
                    'match_end': slot_time + duration,
                })

                slot_time += duration

            current_date += timedelta(days=7)

    def _double_round_robin(self, teams):
        """38 rounds home-away"""
        if len(teams) % 2:
            teams.append(None)

        n = len(teams)
        rounds = []

        for round in range(n - 1):
            pairs = []
            for i in range(n // 2):
                t1 = teams[i]
                t2 = teams[n - 1 - i]
                if t1 and t2:
                    pairs.append((t1, t2))
            teams.insert(1, teams.pop())
            rounds.append(pairs)

        # lượt về đảo sân
        reverse_rounds = [
            [(away, home) for home, away in r]
            for r in rounds
        ]

        return rounds + reverse_rounds