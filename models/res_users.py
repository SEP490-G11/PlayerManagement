from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    team_id = fields.Many2one('football.team', string="Managed Team")