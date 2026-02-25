from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from datetime import date
from payos import PayOS, ItemData, PaymentData
import time




class ZAccountMove(models.Model):
    _inherit = "account.move"
    
    current_qr_amount = fields.Integer(string="Current QR Amount", default=0)
    
    def create_payment_link(self):
        print("current_amount", self.current_qr_amount)
        return {
            'name':_("Create Payment QR"),
            'type': 'ir.actions.client',
            'tag': 'z_payos.create_pr_payment',
            'context': {
                "amount":self.amount_residual,
                "code":self.code,
                "current": self.current_qr_amount,
                "id": self.id,    
            },
            'target': 'new', }
    
    def create_payment_qr(self, amount, code):
        self.ensure_one()
        try:
            client_id = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_payos.z_system_payos_client_id")
            )
            api_key = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_payos.z_system_payos_api_key")
            )
            checksum_key = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_payos.z_system_payos_checksum_key")
            )
            payOS = PayOS(
                client_id=client_id, api_key=api_key, checksum_key=checksum_key
            )
            orderCode = int(time.time())
            
            item = ItemData(
                name=code, quantity=1, price=int(amount)
            )
            paymentData = PaymentData(
                orderCode=orderCode,
                amount=int(amount),
                description= code,
                items=[item],
                cancelUrl="http://localhost:8000",
                returnUrl="http://localhost:8069",
            )

            paymentLinkData = payOS.createPaymentLink(paymentData=paymentData)
            current_qr_amount_new = self.current_qr_amount + 1
            self.write({"current_qr_amount": current_qr_amount_new })    
            return paymentLinkData
        except Exception as e:
            raise ValidationError(_("Error: %s") % e)
        
    
    
    
    def action_register_payment_with_qr(self, amount , code ):
        return self.line_ids.action_register_payment_with_qr(amount, code)
    

        
    class AccountMoveLine(models.Model):
        _inherit = "account.move.line"
        
        
        def action_register_payment_with_qr(self, amount, code):
            ''' Open the account.payment.register wizard to pay the selected journal items.
            :return: An action opening the account.payment.register wizard.
            '''
            return {
                'name': _('Register Payment'),
                'res_model': 'account.payment.register',
                'view_mode': 'form',
                'views': [[False, 'form']],
                'context': {
                    'active_model': 'account.move.line',
                    'active_ids': self.ids,
                    'amount': amount,
                    'code': code,
                    'is_qr_payment': True,
                },
                'target': 'new',
                'type': 'ir.actions.act_window',
            }