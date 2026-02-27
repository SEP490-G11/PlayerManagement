from odoo import models, fields
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

    # =========================================================
    # GENERATE SCHEDULE (EVENLY DISTRIBUTED)
    # =========================================================

    def action_generate_schedule(self):
        self.ensure_one()

        # Xóa lịch cũ
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

        total_days = (self.end_date - self.start_date).days

        if total_days <= 0:
            raise ValidationError("Thời gian mùa giải không hợp lệ.")

        interval_days = total_days / len(rounds)

        duration = timedelta(hours=self.match_duration_hours)

        for index, round_matches in enumerate(rounds):

            # Tính ngày bắt đầu vòng đấu
            round_base_date = self.start_date + timedelta(
                days=int(index * interval_days)
            )

            # Tìm weekday hợp lệ gần nhất
            match_day = None
            for i in range(7):
                candidate = round_base_date + timedelta(days=i)
                if candidate.weekday() in allowed_days:
                    match_day = candidate
                    break

            if not match_day:
                raise ValidationError("Không tìm được ngày hợp lệ.")

            # Bắt đầu đá 16:00
            slot_time = datetime.combine(
                match_day.date(),
                datetime.strptime("16:00", "%H:%M").time()
            )

            for home, away in round_matches:

                self.env['football.match'].create({
                    'season_id': self.id,
                    'home_team_id': home.id,
                    'away_team_id': away.id,
                    'match_date': slot_time,
                    'match_end': slot_time + duration,
                    'state': 'scheduled'
                })

                slot_time += duration

    # =========================================================
    # DOUBLE ROUND ROBIN
    # =========================================================

    def _double_round_robin(self, teams):
        teams = list(teams)

        if len(teams) % 2:
            teams.append(None)

        n = len(teams)
        rounds = []

        # Lượt đi
        for _ in range(n - 1):
            pairs = []
            for i in range(n // 2):
                t1 = teams[i]
                t2 = teams[n - 1 - i]
                if t1 and t2:
                    pairs.append((t1, t2))
            teams.insert(1, teams.pop())
            rounds.append(pairs)

        # Lượt về
        reverse_rounds = [
            [(away, home) for home, away in r]
            for r in rounds
        ]

        return rounds + reverse_rounds