from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
from payos import PayOS, ItemData, PaymentData
import time
from odoo.addons.z_web.helpers.utils import ZUtils


class ZAccountMove(models.Model):
    _inherit = "account.move"

    current_qr_amount = fields.Integer(string="Current QR Amount", default=0)
    log_qr_ids = fields.One2many("z_payos.qr.logs", "move_id", string="Payments")

    def create_payment_link(self):
        self.ensure_one()
        if not self.place_id:
            raise ValidationError(_("Place is required!"))

        return_url = self.place_id.z_system_payos_return_url
        if not return_url:
            raise ValidationError(_("Config return url is required!"))

        return {
            "name": _("Create Payment QR"),
            "type": "ir.actions.client",
            "tag": "z_payos.create_pr_payment",
            "context": {
                "amount": self.amount_residual,
                "code": self.code,
                "current": self.current_qr_amount,
                "id": self.id,
                "return_url": return_url,
            },
            "target": "new",
        }

    def create_payment_qr(self, amount, code):
        self.ensure_one()
        if not self.place_id:
            raise ValidationError(_("Place is required!"))

        try:
            # using sudo to get the place_id
            place = self.sudo().place_id
            client_id = place.z_system_payos_client_id
            api_key = place.z_system_payos_api_key
            checksum_key = place.z_system_payos_checksum_key
            cancel_url = place.z_system_payos_cancel_url
            return_url = place.z_system_payos_return_url
            # tạo hàm kểm tra có thông số cấu hình chưa và rasie lỗi nếu chưa có
            if (
                not client_id
                or not api_key
                or not checksum_key
                or not cancel_url
                or not return_url
            ):
                raise UserError(
                    _("Please configure PayOS settings for place %s!") % place.name
                )

            payOS = PayOS(
                client_id=client_id, api_key=api_key, checksum_key=checksum_key
            )
            orderCode = int(time.time())

            item = ItemData(name=code, quantity=1, price=int(amount))
            paymentData = PaymentData(
                orderCode=orderCode,
                amount=int(amount),
                description=code,
                items=[item],
                cancelUrl=cancel_url,
                returnUrl=return_url,
            )

            paymentLinkData = payOS.createPaymentLink(paymentData=paymentData)
            current_qr_amount_new = self.current_qr_amount + 1
            res_partner_bank = self.env["res.partner.bank"].search(
                [
                    ("bin", "=", paymentLinkData.bin),
                    ("place_id", "=", self.place_id.id),
                ],
                limit=1,
            )
            if not res_partner_bank:
                raise ValidationError(_("Bank account not found!"))
            self.write({"current_qr_amount": current_qr_amount_new})
            qr_payment = (
                self.env["z_payos.qr.logs"]
                .sudo()
                .create(
                    {
                        "payment_amount": amount,
                        "invoice_amount": self.amount_residual,
                        "payment_description": paymentLinkData.description,
                        "bin": paymentLinkData.bin,
                        "payment_code": paymentLinkData.orderCode,
                        "payment_status": "Pending",
                        "move_id": self.id,
                        "place": self.place_id.name,
                        "account_bank": res_partner_bank.acc_number,
                    }
                )
            )
            return {
                "bin": paymentLinkData.bin,
                "checkout_url": paymentLinkData.checkoutUrl,
                "qr_payment_id": qr_payment.id,
                "account_number": paymentLinkData.accountNumber,
                "description": paymentLinkData.description,
                "amount": paymentLinkData.amount,
            }
        except Exception as e:
            raise ValidationError(_("Error: %s") % e)

    def action_register_payment_with_qr(self, amount, code, bin, qr_log_id):
        return self.line_ids.action_register_payment_with_qr(
            amount, code, bin, qr_log_id
        )

    def show_qr_into_counter(self, qr_code_image_url, checkout_url):
        current_user = self.env.user
        channel = f"notification.counter_{current_user.id}"
        self.env["bus.bus"]._sendone(
            channel,
            "notification.counter/qr_event",
            {
                "qr_code_image_url": qr_code_image_url,
                "checkout_url": checkout_url,
                "invoice_ids": [
                    {
                        "id": line.id,
                        "name": line.product_id.name,
                        "quantity": line.quantity,
                        "unit": line.product_uom_id.name,
                        "price_unit": ZUtils.convert_number_to_currency_format(
                            line.price_unit
                        ),
                        "discount": ZUtils.convert_number_to_currency_format(
                            line.discount_amount
                        ),
                    }
                    for line in self.invoice_line_ids
                ],
                "amount": ZUtils.convert_number_to_currency_format(
                    self.amount_residual
                ),
            },
        )

    def action_show_list_invoice_counter(self):
        current_user = self.env.user
        channel = f"notification.counter_{current_user.id}"
        self.env["bus.bus"]._sendone(
            channel,
            "notification.counter/show_invoice_event",
            {
                "invoice_ids": [
                    {
                        "id": line.id,
                        "name": line.product_id.name,
                        "quantity": line.quantity,
                        "unit": line.product_uom_id.name,
                        "price_unit": ZUtils.convert_number_to_currency_format(
                            line.price_unit
                        ),
                        "discount": ZUtils.convert_number_to_currency_format(
                            line.discount_amount
                        ),
                    }
                    for line in self.invoice_line_ids
                ],
                "amount": ZUtils.convert_number_to_currency_format(
                    self.amount_residual
                ),
            },
        )

    def action_open_counter_settings(self):
        settings_record = self.env["z_payos.counter.settings"].search([], limit=1)

        if not settings_record:
            settings_record = self.env["z_payos.counter.settings"].create(
                {
                    "name": "default_setting",
                }
            )

        return {
            "type": "ir.actions.act_window",
            "res_model": "z_payos.counter.settings",
            "view_mode": "form",
            "view_id": self.env.ref("z_payos.view_z_payos_counter_settings_form").id,
            "res_id": settings_record.id,
        }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def action_register_payment_with_qr(self, amount, code, bin, qr_log_id):
        """Open the account.payment.register wizard to pay the selected journal items.
        :return: An action opening the account.payment.register wizard.
        """
        print("mv-id", self.move_id.place_id.id)
        bank_account_id = self.env["res.partner.bank"].search(
            [("bin", "=", bin), ("place_id", "=", self.move_id.place_id.id)]
        )
        return {
            "name": _("Register Payment"),
            "res_model": "account.payment.register",
            "view_mode": "form",
            "views": [[False, "form"]],
            "context": {
                "active_model": "account.move.line",
                "active_ids": self.ids,
                "amount": amount,
                "code": code,
                "is_qr_payment": True,
                "partner_bank_id": bank_account_id.id,
                "qr_log_id": qr_log_id,
            },
            "target": "new",
            "type": "ir.actions.act_window",
        }


class AccountPayment(models.Model):
    _inherit = "account.payment"

    viet_qr_transaction_id = fields.Many2one(
        "z_payos.qr.logs",
        string="Viet QR Transaction",
        store=True,
        domain="[('move_id', '=', move_id),('payment_status','=','Paid'),('is_create_account_payment','=',False)]"
    )   
    
    can_create_qr_payment = fields.Boolean(string="Can Create QR Payment", default=False)
    current_qr_amount = fields.Integer(string="Current QR Amount", default=0)
    
    # New fields for VietQR
    
    @api.depends('state', 'journal_id.qr_code_enabled')
    def _compute_can_create_qr_payment(self):
        for rec in self:
            rec.can_create_qr_payment = (
                rec.state == "draft" and 
                rec.journal_id.qr_code_enabled and
                rec.amount > 0
            )
    
    def _generate_vietqr_reference(self):
        self.ensure_one()
        if not self.partner_id.code:
            raise ValidationError(_("Customer code is required to create VietQR"))
        return f"{self.partner_id.code}/{self.id}"
    
    def create_vietqr(self, amount, code):
        try:
            # Get PayOS configuration
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
            cancel_url = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_payos.z_system_payos_cancel_url")
            )
            return_url = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_payos.z_system_payos_return_url")
            )
            
            if not client_id or not api_key or not checksum_key or not cancel_url or not return_url:
                raise ValidationError(_("Please configure PayOS settings!"))
            
            # Create PayOS payment
            payOS = PayOS(
                client_id=client_id, api_key=api_key, checksum_key=checksum_key
            )
            orderCode = int(time.time())
            
            item = ItemData(name=code, quantity=1, price=int(amount))
            paymentData = PaymentData(
                orderCode=orderCode,
                amount=int(amount),
                description=code,
                items=[item],
                cancelUrl=cancel_url,
                returnUrl=return_url,
            )
            
            paymentLinkData = payOS.createPaymentLink(paymentData=paymentData)
            
            # Update payment record
            current_qr_amount_new = self.current_qr_amount + 1
            self.write({
                "current_qr_amount": current_qr_amount_new,
            })
            
            # Create QR log entry
            qr_payment = self.env["z_payos.qr.logs"].sudo().create({
                "payment_amount": amount,
                "invoice_amount": amount,
                "payment_description": code,
                "account_bank": paymentLinkData.bin,
                "payment_code": paymentLinkData.orderCode,
                "payment_status": "Pending",
                "payment_id": self.id,
            })
            
            return {
                "bin": paymentLinkData.bin,
                "checkout_url": paymentLinkData.checkoutUrl,
                "qr_payment_id": qr_payment.id,
                "account_number": paymentLinkData.accountNumber,
                "description": paymentLinkData.description,
                "amount": paymentLinkData.amount,
            }
        except Exception as e:
            raise ValidationError(_("Error: %s") % e)
            
    
    def create_payment_link(self):
        self.ensure_one()
    
        # Check conditions
        if self.payment_type != "inbound":
            raise ValidationError(_("Payment type must be inbound"))
        
        if self.state != "draft":
            raise ValidationError(_("Payment must be in draft state to create VietQR"))
        
        if not self.journal_id.qr_code_enabled:
            raise ValidationError(_("Payment method must have QR code enabled"))
        
        if self.amount <= 0:
            raise ValidationError(_("Payment amount must be greater than 0"))
        
        if self.currency_id.name != "VND":
            raise ValidationError(_("Payment amount must be in VND"))
        
 
        
        return_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("z_payos.z_system_payos_return_url")
        )
        

        return {
            "name": _("Create Payment QR"),
            "type": "ir.actions.client",
            "tag": "z_payos.create_qr_account_payment",
            "context": {
                "amount": self.amount,
                "code": self._generate_vietqr_reference(),
                "current": self.current_qr_amount,
                "id": self.id,
                "return_url": return_url,
            },
            "target": "new",
        }
        
    def action_vietqr_post(self, bin, qr_log_id):
        self.ensure_one()
        qr_log = self.env["z_payos.qr.logs"].browse(qr_log_id)
        qr_log.write({"payment_status": "Paid"})
        journal_id = self.env["account.journal"].search([("bank_account_id.acc_number", "=", bin)], limit=1)
        if not journal_id:
            raise ValidationError(_("Journal not found"))
        
        self.write({
            "journal_id": journal_id.id,
            "viet_qr_transaction_id": qr_log_id,
        })
        return super(AccountPayment, self).action_post()
    
    def action_open_counter_settings(self):
        settings_record = self.env['z_payos.counter.settings'].search([], limit=1)

        if not settings_record:
            settings_record = self.env['z_payos.counter.settings'].create({
                'name': 'default_setting',
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'z_payos.counter.settings',
            'view_mode': 'form',
            'view_id': self.env.ref('z_payos.view_z_payos_counter_settings_form').id,
            'res_id': settings_record.id,
        }
        
    
    def create(self, vals):
        # Check if vals is a list of dictionaries
        if isinstance(vals, list):
            for item in vals:
                if isinstance(item, dict) and "viet_qr_transaction_id" in item:
                    qr_logs = self.env["z_payos.qr.logs"].search(
                        [("id", "=", item["viet_qr_transaction_id"])]
                    )
                    if qr_logs:
                        qr_logs.write({"is_create_account_payment": True})
                    break
        return super(AccountPayment, self).create(vals)
