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

    @api.constrains('start_date', 'end_date')
    def _check_season_duration(self):
        for rec in self:
            if not rec.start_date or not rec.end_date:
                continue

            if rec.end_date <= rec.start_date:
                raise ValidationError("Ngày kết thúc phải sau ngày bắt đầu.")

            delta = rec.end_date - rec.start_date
            total_weeks = delta.days // 7

            if total_weeks < 38:
                raise ValidationError(
                    "Mùa giải phải kéo dài tối thiểu 38 tuần."
                )

    def action_generate_schedule(self):
        self.ensure_one()

        self.match_ids.unlink()

        teams = list(self.env['football.team'].search([]))

        if len(teams) != 20:
            raise ValidationError("EPL cần đúng 20 đội.")

        rounds = self._double_round_robin(teams)

        if len(rounds) != 38:
            raise ValidationError("Phải có đúng 38 vòng.")

        if not self.allowed_weekday_ids:
            raise ValidationError("Phải chọn ít nhất một weekday.")

        allowed_days = sorted(self.allowed_weekday_ids.mapped('code'))

        duration = timedelta(hours=self.match_duration_hours)

        current_date = self.start_date

        for round_matches in rounds:

            match_day = None
            for i in range(7):
                candidate = current_date + timedelta(days=i)
                if candidate.weekday() in allowed_days:
                    match_day = candidate
                    break

            if not match_day:
                raise ValidationError("Không tìm được ngày hợp lệ.")

            slot_time = datetime.combine(
                match_day.date(),
                datetime.strptime("16:00", "%H:%M").time()
            )

            for home, away in round_matches:
                self.env['football.match'].with_context(
                    skip_conflict_check=True
                ).create({
                    'season_id': self.id,
                    'home_team_id': home.id,
                    'away_team_id': away.id,
                    'match_date': slot_time,
                    'match_end': slot_time + duration,
                    'state': 'scheduled'
                })

                slot_time += duration

            current_date += timedelta(days=7)

    def _double_round_robin(self, teams):
        teams = list(teams)

        if len(teams) % 2:
            teams.append(None)

        n = len(teams)
        rounds = []

        for _ in range(n - 1):
            pairs = []
            for i in range(n // 2):
                t1 = teams[i]
                t2 = teams[n - 1 - i]
                if t1 and t2:
                    pairs.append((t1, t2))
            teams.insert(1, teams.pop())
            rounds.append(pairs)

        reverse_rounds = [
            [(away, home) for home, away in r]
            for r in rounds
        ]

        return rounds + reverse_rounds