from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


# =====================================================
# TEAM
# =====================================================

class Team(models.Model):
    _name = 'football.team'
    _description = 'Football Team'

    name = fields.Char(string="Tên đội bóng", required=True)
    coach = fields.Char(string="Huấn luyện viên")
    founded_year = fields.Integer(string="Năm thành lập")

    # Relations
    player_ids = fields.One2many(
        'football.player',
        'team_id',
        string="Cầu thủ"
    )

    contract_ids = fields.One2many(
        'football.contract',
        'team_id',
        string="Hợp đồng"
    )

    # Tổng giá trị cầu thủ
    total_market_value = fields.Float(
        string="Tổng giá trị đội",
        compute="_compute_total_value",
        store=True
    )

    # Tổng quỹ lương (chỉ tính contract active)
    total_salary = fields.Float(
        string="Tổng quỹ lương",
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
            active_contracts = team.contract_ids.filtered(
                lambda c: c.state == 'active'
            )
            team.total_salary = sum(
                active_contracts.mapped('salary')
            )


# =====================================================
# PLAYER
# =====================================================

class Player(models.Model):
    _name = 'football.player'
    _description = 'Football Player'

    name = fields.Char(string="Tên cầu thủ", required=True)
    age = fields.Integer(string="Tuổi")

    position = fields.Selection([
        ('gk', 'Thủ môn'),
        ('df', 'Hậu vệ'),
        ('mf', 'Tiền vệ'),
        ('fw', 'Tiền đạo')
    ], string="Vị trí")

    number = fields.Integer(string="Số áo")
    nationality = fields.Char(string="Quốc tịch")
    market_value = fields.Float(string="Giá trị chuyển nhượng")

    team_id = fields.Many2one(
        'football.team',
        string="Đội bóng"
    )

    image = fields.Binary(string="Ảnh cầu thủ")

    # ===== VALIDATION =====

    @api.constrains('age')
    def _check_age(self):
        for rec in self:
            if rec.age and (rec.age < 15 or rec.age > 50):
                raise ValidationError(
                    "Tuổi cầu thủ phải từ 15 đến 50."
                )

    @api.constrains('number', 'team_id')
    def _check_unique_number(self):
        for rec in self:
            if rec.number and rec.team_id:
                domain = [
                    ('number', '=', rec.number),
                    ('team_id', '=', rec.team_id.id),
                    ('id', '!=', rec.id)
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(
                        "Số áo đã tồn tại trong đội bóng này!"
                    )


# =====================================================
# CONTRACT
# =====================================================

class FootballContract(models.Model):
    _name = 'football.contract'
    _description = 'Football Contract'

    player_id = fields.Many2one(
        'football.player',
        string="Cầu thủ",
        required=True
    )

    team_id = fields.Many2one(
        'football.team',
        string="Đội bóng",
        required=True
    )

    date_start = fields.Date(
        string="Ngày bắt đầu",
        required=True
    )

    date_end = fields.Date(
        string="Ngày kết thúc",
        required=True
    )

    salary = fields.Float(
        string="Lương",
        required=True
    )

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired')
    ],
        compute="_compute_state",
        store=True
    )

    # ===== Auto trạng thái =====

    @api.depends('date_end')
    def _compute_state(self):
        today = date.today()
        for rec in self:
            if rec.date_end and rec.date_end < today:
                rec.state = 'expired'
            else:
                rec.state = 'active'

    # ===== Không cho 2 hợp đồng active =====

    @api.constrains('player_id', 'date_start', 'date_end')
    def _check_duplicate_active_contract(self):
        for rec in self:
            domain = [
                ('player_id', '=', rec.player_id.id),
                ('id', '!=', rec.id),
                ('state', '=', 'active')
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(
                    "Cầu thủ đã có hợp đồng đang hiệu lực."
                )