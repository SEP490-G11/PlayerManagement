from odoo import models, fields, _
import time


class PartnerBank(models.Model):
    _inherit = "res.partner.bank"
    
    bin = fields.Char("Bin", help="Bank Identification Number for PayOS")
    place_id = fields.Many2one("z_place.place", string="Place")
    