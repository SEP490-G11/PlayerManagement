from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    qr_code_enabled = fields.Boolean(
        string="Enable QR Code",
        default=False,
        compute="_qr_code_enabled_compute"
    ) 
    
    def _qr_code_enabled_compute(self):
        for rec in self:
            rec.qr_code_enabled = True if rec.bank_account_id else False
            
            