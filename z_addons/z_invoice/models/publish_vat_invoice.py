from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
import logging
import requests
import json
from odoo.addons.z_invoice.helpers.utils import ZInvoiceUtils   
from odoo.addons.z_invoice.helpers.misa_utils import ZMISAUtils

_logger = logging.getLogger(__name__)

class ZPublishVATInvoice(models.Model):
    _name = "z_invoice.publish_vat_invoice"
    _description = "Publish VAT Invoice"
    _order = "create_date desc"

    name = fields.Char(string="Name")
    invoice_id = fields.Many2one(string="Invoice", comodel_name="account.move")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner", related="invoice_id.partner_id")
    place_id = fields.Many2one(string="Place", comodel_name="z_place.place", related="invoice_id.place_id")
    customer_company_id = fields.Many2one(string="Customer Company", comodel_name="res.company")
    customer_company_name = fields.Char(string="Customer Company Name", related="customer_company_id.name")
    customer_company_tax_code = fields.Char(string="Customer Company Tax Code", related="customer_company_id.vat")
    customer_company_address = fields.Char(string="Customer Company Address", related="customer_company_id.street")
    customer_company_bank_account = fields.Char(string="Customer Company Bank Account", related="customer_company_id.bank_ids.acc_number")
    misa_template_id = fields.Many2one(
        "z_invoice.misa_invoice_template",
        string="MISA Template"
    )
    url = fields.Char(string="URL")
    is_ticket = fields.Boolean(string="Is Ticket", default=False)
    transaction_id = fields.Char(string="Transaction ID")
    misa_inv_no = fields.Char(string="MISA Invoice No")
    misa_inv_code = fields.Char(string="MISA Invoice Code")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled')
    ], string="State", default="draft")

    @api.depends('partner_id')
    def _compute_customer_company_id(self):
        for record in self:
            if record.partner_id.company_id:
                record.customer_company_id = record.partner_id.company_id
            else:
                record.customer_company_id = False

    @api.constrains('company_name', 'tax_code', 'address')
    def _check_company_info_required(self):
        for record in self:
            if record.company_name or record.tax_code:
                if not record.company_name or not record.tax_code or not record.address:
                    raise ValidationError(_(
                        "Nếu có thông tin Tên công ty hoặc Mã số thuế, "
                        "thì bắt buộc phải có đầy đủ: Tên công ty, Mã số thuế, và Địa chỉ"
                    )) 

    @api.model
    def get_misa_templates(self):
        try:
            url = "https://testapi.meinvoice.vn/api/integration/invoice/templates"
            params = {
                'invoiceWithCode': 'true',
                'ticket': 'false',
                'year': '2024'
            }
            headers = {
                'Authorization': f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJBcHBJZCI6ImFjNjIwZmUyLWRmYTQtNDQ4MC1hNTU3LWFkMGFkOGI4MmZlMyIsIkNvbXBhbnlJZCI6IjExNDA1NiIsIlJvbGVUeXBlIjoiMSIsIlVzZXJJZCI6IjRlMTEzNDQ1LTQxYmItNGViZS1hOWM1LTQ2YThhZTkzNzdmMCIsIlVzZXJOYW1lIjoidGVzdG1pc2FAeWFob28uY29tIiwiTWlzYUlkIjoiYTkxZjA3ODEtMzE3Ny00NmFmLWI5YmItZjFiOWVmNzY3MjI4IiwiUGhvbmVOdW1iZXIiOiIwOTcxNTAwNzMxIiwiRW1haWwiOiJ0ZXN0bWlzYUB5YWhvby5jb20iLCJUYXhDb2RlIjoiNjg2ODY4Njg2OC01NjAiLCJTZWN1cmVUb2tlbiI6IlRtOElJaVF5dFhSTXQwL2V3SlZlL2lFMHg5UFFjV3QrUkFTN0JGNWNPZ2diRmJGamNIeUJ1TnV1Q2ZBMnI0amYiLCJuYmYiOjE3NTE1MTcyOTUsImV4cCI6MTc1NDEwOTI5NSwiaWF0IjoxNzUxNTE3Mjk1LCJpc3MiOiJodHRwczovL21laW52b2ljZS52biIsImF1ZCI6Imh0dHBzOi8vbWVpbnZvaWNlLnZuIn0.fCb0_Btq0y5Rfv3OFaEmG0rsll9eXYFrS_MKRyq277U',
                'Content-Type': 'application/json'
            }

            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('success'):
                templates_data = json.loads(data.get('data', '[]'))
                return {
                    'success': True,
                    'data': templates_data
                }
            else:
                return {
                    'success': False,
                    'error': data.get('descriptionErrorCode', 'Unknown error')
                }
        except Exception as e:
            _logger.error(f"Unexpected error: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def action_preview_unpublish_invoice(self):
        self.ensure_one()
        data = self._prepare_invoice_data()
        token = self._get_misa_token()
        response = ZMISAUtils.call_invoice_unpublish_api(token, data, self.env)

        if response.get("success") and response.get("data"):
            preview_url = response["data"]
            if preview_url:
                return {
                    'type': 'ir.actions.act_url',
                    'url': preview_url,
                    'target': 'new',
                }
            else:
                raise UserError("No preview URL returned from MISA API.")
        else:
            raise UserError(response.get("error") or "API call failed")

    def action_publish_vat_invoice(self):
        self.ensure_one()

        if self.state == "published":
            raise UserError("Hóa đơn đã được phát hành")

        self.state = "published"

        data = {
            "SignType": 2,
            "InvoiceData": [
                self._prepare_invoice_data()
            ],
            "PublishInvoiceData": None,
        } 
        token = self._get_misa_token()
        response = ZMISAUtils.call_invoice_publish_api(token, data)

        if response.get("success"):
            created_invoice = response["createInvoiceResult"]
            publish_invoice = response["publishInvoiceResult"]
            if created_invoice:
                self.transaction_id = json.loads(created_invoice)[0]["TransactionID"]
                self.misa_inv_no = json.loads(created_invoice)[0]["InvNo"]
                self.misa_inv_code = json.loads(created_invoice)[0]["InvCode"]
            else:
                self.transaction_id = json.loads(publish_invoice)[0]["TransactionID"]
                self.misa_inv_no = json.loads(publish_invoice)[0]["InvNo"]
                self.misa_inv_code = json.loads(publish_invoice)[0]["InvCode"]
            self.action_preview_publish_invoice()
            self.invoice_id.is_publish_vat_invoice = True
            return {
                    "type": "ir.actions.client",
                    "tag": "reload",
                }
        else:
            raise UserError(response.get("error") or "API call failed")

    def _prepare_invoice_data(self):
        if not self.misa_template_id:
            raise UserError("MISA template is required")

        original_invoice_detail = []
        for index, line in enumerate(self.invoice_id.invoice_line_ids):
            original_invoice_detail.append({
                "ItemType": 1,
                "LineNumber": index + 1,
                "SortOrder": index + 1,
                "ItemCode": line.product_id.default_code or "",
                "ItemName": line.product_id.name or "",
                "UnitName": line.product_id.uom_id.name or "",
                "Quantity": line.quantity or 0,
                "UnitPrice": line.price_unit or 0,
                "DiscountRate": line.discount or 0,
                "DiscountAmountOC": line.price_subtotal * line.discount / 100,
                "DiscountAmount": line.price_subtotal * (line.discount or 0) / 100,
                "AmountOC": line.price_total or 0,
                "Amount": line.price_total or 0,
                "AmountWithoutVATOC": line.price_subtotal or 0,
                "AmountWithoutVAT": line.price_subtotal or 0,
                "VATRateName": line.tax_ids.name or "",
                "VATAmountOC": line.price_total - line.price_subtotal,
                "VATAmount": line.price_total - line.price_subtotal,
            })

        return {
            "RefID": self.invoice_id.name or "",
            "InvSeries": self.misa_template_id.inv_series or "",
            "InvoiceName": self.misa_template_id.template_name or "",
            "InvDate": self.invoice_id.date.strftime("%Y-%m-%d") if self.invoice_id.date else "",
            "CurrencyCode": "VND",
            "ExchangeRate": 1,
            "PaymentMethodName": "TM/CK",
            "IsTicket": False,
            "BuyerLegalName": self.customer_company_name or "",
            "BuyerTaxCode": self.customer_company_tax_code or "",
            "BuyerAddress": self.customer_company_address or "",
            "BuyerBankAccount": self.customer_company_bank_account or "",
            "BuyerPhoneNumber": self.partner_id.mobile or "",
            "BuyerEmail": self.partner_id.email or "",
            "TotalSaleAmountOC": self.invoice_id.amount_untaxed or 0.0,
            "TotalSaleAmount": self.invoice_id.amount_untaxed or 0.0,
            "TotalDiscountAmountOC": self.invoice_id.total_discount or 0.0,  # Nếu bạn có custom field này
            "TotalDiscountAmount": self.invoice_id.total_discount or 0.0,    # Nếu không có thì phải tính thủ công
            "TotalAmountWithoutVATOC": self.invoice_id.amount_untaxed or 0.0,
            "TotalAmountWithoutVAT": self.invoice_id.amount_untaxed or 0.0,
            "TotalVATAmountOC": self.invoice_id.amount_tax or 0.0,
            "TotalVATAmount": self.invoice_id.amount_tax or 0.0,
            "TotalAmountOC": self.invoice_id.amount_total or 0.0,
            "TotalAmount": self.invoice_id.amount_total or 0.0,
            "TotalAmountInWords": (
                ZInvoiceUtils.convert_number_to_vietnamese(
                    int(self.invoice_id.total_after_discount)
                ) + " đồng."
                if self.invoice_id.total_after_discount else ""
            ),
            "OriginalInvoiceDetail": original_invoice_detail,
            "TaxRateInfo": [
                {
                    "VATRateName": "",
                    "AmountWithoutVATOC": self.invoice_id.amount_untaxed or 0.0,
                    "VATAmountOC": self.invoice_id.amount_tax or 0.0
                }
            ]
        }

    def action_preview_publish_invoice(self):
        self.ensure_one()
        if not self.url:
            token = self._get_misa_token()
            # Call the API using ZMISAUtilsx
            response = ZMISAUtils.call_preview_published_invoice_api(token, [self.transaction_id])

            # Handle the response
            if response.get("success") and response.get("data"):
                preview_url = response["data"]
                if preview_url:
                    self.url = preview_url  # Make sure you have this field in your model

                else:
                    raise UserError("No preview URL returned from MISA API.")
            else:
                raise UserError(response.get("error") or "API call failed")
            

    def _get_misa_token(self):
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJBcHBJZCI6ImFjNjIwZmUyLWRmYTQtNDQ4MC1hNTU3LWFkMGFkOGI4MmZlMyIsIkNvbXBhbnlJZCI6IjExNDA1NiIsIlJvbGVUeXBlIjoiMSIsIlVzZXJJZCI6IjRlMTEzNDQ1LTQxYmItNGViZS1hOWM1LTQ2YThhZTkzNzdmMCIsIlVzZXJOYW1lIjoidGVzdG1pc2FAeWFob28uY29tIiwiTWlzYUlkIjoiYTkxZjA3ODEtMzE3Ny00NmFmLWI5YmItZjFiOWVmNzY3MjI4IiwiUGhvbmVOdW1iZXIiOiIwOTcxNTAwNzMxIiwiRW1haWwiOiJ0ZXN0bWlzYUB5YWhvby5jb20iLCJUYXhDb2RlIjoiNjg2ODY4Njg2OC01NjAiLCJTZWN1cmVUb2tlbiI6IlRtOElJaVF5dFhSTXQwL2V3SlZlL2lFMHg5UFFjV3QrUkFTN0JGNWNPZ2diRmJGamNIeUJ1TnV1Q2ZBMnI0amYiLCJuYmYiOjE3NTE4MTI3ODAsImV4cCI6MTc1NDQwNDc4MCwiaWF0IjoxNzUxODEyNzgwLCJpc3MiOiJodHRwczovL21laW52b2ljZS52biIsImF1ZCI6Imh0dHBzOi8vbWVpbnZvaWNlLnZuIn0.bf8ZzAqH6Gwfd3GUvzpXY9tXocacFWl_xbQiJe20Ehg"
