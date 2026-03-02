from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FootballMatch(models.Model):
    _name = 'football.match'
    _description = 'Football Match'
    _order = 'match_date asc'

    season_id = fields.Many2one('football.season', required=True)

    home_team_id = fields.Many2one('football.team', required=True)
    away_team_id = fields.Many2one('football.team', required=True)

    match_date = fields.Datetime(required=True)
    match_end = fields.Datetime(required=True)

    home_score = fields.Integer()
    away_score = fields.Integer()

    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('played', 'Played'),
        ('cancelled', 'Cancelled')
    ], default='scheduled')

    # ==========================================
    # AUTO UPDATE STATE WHEN CREATING
    # ==========================================

    @api.model
    def create(self, vals):
        now = fields.Datetime.now()

        match_end = vals.get('match_end')
        home_score = vals.get('home_score')
        away_score = vals.get('away_score')

        if match_end and match_end <= now:
            if home_score is not None and away_score is not None:
                vals['state'] = 'played'

        return super().create(vals)

    # ==========================================
    # WRITE
    # ==========================================

    def write(self, vals):
        now = fields.Datetime.now()

        restricted_fields = [
            'home_score',
            'away_score',
            'home_team_id',
            'away_team_id',
            'match_date',
            'match_end'
        ]

        for rec in self:
            # Không cho sửa nếu trận chưa bắt đầu
            if rec.match_date and now < rec.match_date:
                if any(field in vals for field in restricted_fields):
                    raise ValidationError(
                        "Chỉ được chỉnh sửa khi trận đã bắt đầu."
                    )

        # Nếu có sửa score -> tự set played nếu đã qua match_end
        if 'home_score' in vals or 'away_score' in vals:
            for rec in self:
                home = vals.get('home_score', rec.home_score)
                away = vals.get('away_score', rec.away_score)

                if (
                    rec.match_end
                    and rec.match_end <= now
                    and home is not None
                    and away is not None
                ):
                    vals['state'] = 'played'

        return super().write(vals)

    # ==========================================
    # CRON: AUTO UPDATE STATE REAL-TIME
    # ==========================================

    def _cron_auto_update_played(self):
        now = fields.Datetime.now()

        matches = self.search([
            ('state', '=', 'scheduled'),
            ('match_end', '<=', now)
        ])

        for match in matches:
            if match.home_score is not None and match.away_score is not None:
                match.state = 'played'

        if matches:
            teams = self.env['football.team'].search([])
            teams._compute_stats()

    # ==========================================
    # VALIDATIONS
    # ==========================================

    @api.constrains('home_team_id', 'away_team_id')
    def _check_same_team(self):
        for rec in self:
            if rec.home_team_id == rec.away_team_id:
                raise ValidationError("Hai đội không được trùng.")

    @api.constrains('match_date', 'match_end',
                    'home_team_id', 'away_team_id', 'season_id')
    def _check_conflict(self):

        for rec in self:

            if not rec.match_date or not rec.match_end:
                continue

            if rec.match_end <= rec.match_date:
                raise ValidationError(
                    "Thời gian kết thúc phải sau thời gian bắt đầu."
                )

            domain = [
                ('id', '!=', rec.id),
                ('season_id', '=', rec.season_id.id),
                '|',
                ('home_team_id', 'in',
                 [rec.home_team_id.id, rec.away_team_id.id]),
                ('away_team_id', 'in',
                 [rec.home_team_id.id, rec.away_team_id.id]),
                ('match_date', '<', rec.match_end),
                ('match_end', '>', rec.match_date),
            ]

            if self.search_count(domain):
                raise ValidationError(
                    "Đội bị trùng lịch thi đấu trong khoảng thời gian này."
                )