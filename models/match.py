from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo import fields
from odoo.exceptions import ValidationError

class FootballMatch(models.Model):
    _name = 'football.match'
    _description = 'Football Match'
    _order = 'match_date asc'

    season_id = fields.Many2one(
        'football.season',
        required=True
    )

    home_team_id = fields.Many2one(
        'football.team',
        required=True
    )

    away_team_id = fields.Many2one(
        'football.team',
        required=True
    )

    match_date = fields.Datetime(required=True)
    match_end = fields.Datetime(required=True)

    home_score = fields.Integer()
    away_score = fields.Integer()

    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('played', 'Played'),
        ('cancelled', 'Cancelled')
    ], default='scheduled')
    
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

            # Nếu trận CHƯA bắt đầu
            if rec.match_date and now < rec.match_date:

                if any(field in vals for field in restricted_fields):
                    raise ValidationError(
                        "Chỉ được chỉnh sửa khi trận đã bắt đầu."
                    )

        return super().write(vals)

    # =============================
    # Không cho 2 đội trùng nhau
    # =============================
    @api.constrains('home_team_id', 'away_team_id')
    def _check_same_team(self):
        for rec in self:
            if rec.home_team_id == rec.away_team_id:
                raise ValidationError("Hai đội không được trùng.")

    # =============================
    # Không cho trùng lịch theo KHOẢNG THỜI GIAN
    # =============================
    @api.constrains('match_date', 'match_end', 'home_team_id', 'away_team_id')
    def _check_conflict(self):
        for rec in self:
            if not rec.match_date or not rec.match_end:
                continue

            domain = [
                ('id', '!=', rec.id),
                ('season_id', '=', rec.season_id.id),
                ('match_date', '<', rec.match_end),
                ('match_end', '>', rec.match_date),
                '|',
                ('home_team_id', 'in', [rec.home_team_id.id, rec.away_team_id.id]),
                ('away_team_id', 'in', [rec.home_team_id.id, rec.away_team_id.id]),
            ]

            if self.search_count(domain):
                raise ValidationError("Đội bị trùng lịch thi đấu trong khoảng thời gian này.")  
    @api.onchange('home_score', 'away_score')
    def _auto_set_played(self):
        if self.home_score is not None and self.away_score is not None:
            self.state = 'played'        