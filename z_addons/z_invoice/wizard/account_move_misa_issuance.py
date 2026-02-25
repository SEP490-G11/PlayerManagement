# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.addons.z_invoice.helpers.misa_utils import ZMISAUtils
from odoo.addons.z_invoice.helpers.utils import ZInvoiceUtils
import datetime
import json
import re

class AccountMoveMisaIssuanceWizard(models.TransientModel):
    _name = 'account.move.misa.issuance'
    _description = 'MISA Issuance Wizard'

    
    move_id = fields.Many2one('account.move', string="Invoice", required=True)
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner", related="move_id.partner_id")
    place_id = fields.Many2one(string="Place", comodel_name="z_place.place", related="move_id.place_id")
    customer_company_id = fields.Many2one("res.company", string="Customer Company")
    customer_company_name = fields.Char(string="Customer Company Name")
    customer_company_tax_code = fields.Char(string="Customer Company Tax Code")
    customer_company_address = fields.Char(string="Customer Company Address")
    customer_company_bank_account = fields.Char(string="Customer Company Bank Account")
    customer_email = fields.Char(string="Customer Email")
    misa_template_id = fields.Many2one(
        "z_invoice.misa_invoice_template",
        string="MISA Template"
    )
    
    note = fields.Text(string="Note")
    
    @api.onchange("move_id")
    def _onchange_move_id(self):
        self.ensure_one()
        if self.move_id:
            self.customer_company_id = self.move_id.partner_id.company_id
            self.customer_company_name = self.move_id.partner_id.company_name
            self.customer_company_tax_code = self.move_id.partner_id.vat
            self.customer_company_address = self.move_id.partner_id.street
            self.customer_email = self.move_id.partner_id.email
            self.customer_company_bank_account = self.move_id.partner_id.bank_ids[0].acc_number if self.move_id.partner_id.bank_ids else ""
            self.misa_template_id = self.move_id.misa_template_id
            self.note = self.move_id.note

    def _validate_misa_issuance(self):
        # Validate company fields
        self._validate_company_fields()
        # Validate MISA state
        self._validate_misa_state()
        # Validate time constraint for adjustment and replacement invoices
        self._validate_time_constraint()
        
    def _validate_time_constraint(self):
        """Validate that adjustment and replacement invoices are published within 1 day of original invoice"""
        if self.move_id.misa_type_inv in ["1", "2"]:  # Replacement or Adjustment
            original_invoice = None
            if self.move_id.misa_type_inv == "1":  # Replacement
                original_invoice = self.move_id.origin_move_id
            elif self.move_id.misa_type_inv == "2":  # Adjustment
                original_invoice = self.move_id.reversed_entry_id
            
            if original_invoice and original_invoice.publish_misa_invoice_date:
                # Calculate time difference
                current_date = fields.Date.today()
                original_date = original_invoice.publish_misa_invoice_date
                days_diff = (current_date - original_date).days
                
                if days_diff > 1:
                    raise UserError(_(
                        "Hóa đơn %s chỉ có thể được phát hành trong vòng 1 ngày kể từ ngày hóa đơn gốc (%s) được phát hành. "
                        "Hiện tại đã qua %d ngày." % (
                            "thay thế" if self.move_id.misa_type_inv == "1" else "điều chỉnh",
                            original_date.strftime("%d/%m/%Y"),
                            days_diff
                        )
                    ))
    
    def _validate_misa_state(self):
        if self.move_id.misa_type_inv == "3":
            raise UserError(_("Invoice has been cancelled"))
        if self.move_id.misa_type_inv == "1" and not self.move_id.origin_move_id.misa_state == "published":
            raise UserError(_("Origin invoice has not been published"))
        if self.move_id.misa_type_inv == "2" and not self.move_id.reversed_entry_id.misa_state == "published":
            raise UserError(_("Origin invoice has not been published"))
        if self.customer_email: 
            if not re.match(r"[^@]+@[^@]+\.[^@]+", self.customer_email):
                raise UserError(_("Invalid email address"))        
        
    def _validate_company_fields(self):
        has_company_name = bool(self.customer_company_name and self.customer_company_name.strip())
        has_tax_code = bool(self.customer_company_tax_code and self.customer_company_tax_code.strip())
        has_address = bool(self.customer_company_address and self.customer_company_address.strip())
        
        # Check if any field has a value
        if has_company_name or has_tax_code:
            missing_fields = []
            
            if not has_company_name:
                missing_fields.append(_("customer company name"))
            if not has_tax_code:
                missing_fields.append(_("customer company tax code"))
            if not has_address:
                missing_fields.append(_("customer company address"))
            
            if missing_fields:
                raise UserError(_(
                    "If one of Company Name, Tax ID, or Company Address is filled, all three must be filled!"
                ))
        
    def action_publish(self):
        self.ensure_one()
        if not self.misa_template_id:
            raise UserError(_("MISA template is required"))
        if self.move_id.misa_state == "published":
            raise UserError(_("Invoice has been published"))
        if self.move_id.state != "posted":
            raise UserError(_("Invoice is not posted"))
        if self.move_id.misa_state == "cancelled":
            raise UserError(_("Invoice has been cancelled"))      
        # Validate company fields
        self._validate_misa_issuance()
        
        data = {
            "SignType": 2,
            "InvoiceData": [
                self._prepare_invoice_data()
            ],
            "PublishInvoiceData": None,
        }
        self.move_id.is_call_to_misa = True
        self.env.cr.commit()
        
        token = self._get_misa_token()
        response = ZMISAUtils.call_invoice_publish_api(token, data, self.env)
        
        is_success, error_code, invoice_error_code, invoice_data = self._handle_publish_invoice_response(response)
        
        if is_success and not invoice_error_code:
            transaction_id = invoice_data.get("TransactionID")
            inv_no = invoice_data.get("InvNo")
            inv_code = invoice_data.get("InvCode")

            self.move_id.misa_transaction_id = transaction_id
            self.move_id.misa_inv_no = inv_no
            self.move_id.misa_inv_code = inv_code
            self.move_id.is_publish_vat_invoice = True
            self.move_id.misa_state = "published"
            self.move_id.misa_template_id = self.misa_template_id
            self.move_id.publish_misa_invoice_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            self.env.cr.commit()
      

            url = self._get_preview_publish_invoice_url(transaction_id)
            self.move_id.misa_url = url
            if self.customer_company_name:
                self._update_company_info()
            
            self.move_id.is_call_to_misa = False
            self.env.cr.commit()
            
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _("Invoice published successfully!"),
                    "type": "success",
                    "sticky": False,
                    "next": {
                        "type": "ir.actions.act_window_close"
                    }
                }
            }
        else:
            self.move_id.is_call_to_misa = False
            self.env.cr.commit()
            raise UserError(invoice_error_code or error_code or "API call failed")
        
    
    def _get_preview_publish_invoice_url(self, transaction_id):
        if not self.move_id.misa_url:
            token = self._get_misa_token()
            response = ZMISAUtils.call_preview_published_invoice_api(token, [transaction_id], self.env)
            if response.get("success") and response.get("data"):
                preview_url = response["data"]
                if preview_url:
                    return preview_url

                else:
                    raise UserError("Bạn đã hoàn thành việc phát hành hóa đơn. Nhưng gặp lỗi trong quá trình lấy URL.")
            else:
                raise UserError(response.get("ErrorCode") or "Gặp lỗi trong quá trình lấy URL.")

    
    def action_preview_unpublish_invoice(self):
        if not self.misa_template_id:
            raise UserError("MISA template is required")
        self.ensure_one()
        
        # Validate company fields
        self._validate_misa_issuance()
        
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
                raise UserError(_("No preview URL returned from MISA API."))
        else:
            raise UserError(response.get("error") or "API call failed")
    
    
    def _prepare_invoice_data(self):
        original_invoice_detail = []
        for index, line in enumerate(self.move_id.invoice_line_ids):
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
                "VATRateName": line.tax_ids.name or "0%",
                "VATAmountOC": line.price_total - line.price_subtotal,
                "VATAmount": line.price_total - line.price_subtotal,
            })

        data = {
            "RefID": self.move_id.code or "",
            "InvSeries": self.misa_template_id.inv_series or "",
            "InvoiceName": self.misa_template_id.template_name or "",
            "InvDate": self.move_id.invoice_date.strftime("%Y-%m-%d") if self.move_id.invoice_date else "",
            "CurrencyCode": "VND",
            "ExchangeRate": 1,
            "PaymentMethodName": "TM/CK",
            "IsTicket": True if (self.customer_email or self.partner_id.email) else False,
            "BuyerLegalName": self.customer_company_name or self.partner_id.company_name or "",
            "BuyerTaxCode": self.customer_company_tax_code or self.partner_id.vat or "",
            "BuyerAddress": self.customer_company_address or self.partner_id.street or "",
            "BuyerBankAccount": self.customer_company_bank_account or self.partner_id.bank_ids.acc_number or "",
            "BuyerPhoneNumber": self.partner_id.mobile or "",
            "BuyerFullName": self.partner_id.name or "",
            "BuyerEmail": self.customer_email or self.partner_id.email or "",
            "TotalSaleAmountOC": self.move_id.amount_untaxed or 0.0,
            "TotalSaleAmount": self.move_id.amount_untaxed or 0.0,
            "TotalDiscountAmountOC": self.move_id.total_discount or 0.0,
            "TotalDiscountAmount": self.move_id.total_discount or 0.0,
            "TotalAmountWithoutVATOC": self.move_id.amount_untaxed or 0.0,
            "TotalAmountWithoutVAT": self.move_id.amount_untaxed or 0.0,
            "TotalVATAmountOC": self.move_id.amount_tax or 0.0,
            "TotalVATAmount": self.move_id.amount_tax or 0.0,
            "TotalAmountOC": self.move_id.amount_total or 0.0,
            "TotalAmount": self.move_id.amount_total or 0.0,
            #Uppercase first letter
            "TotalAmountInWords": (
                ZInvoiceUtils.convert_number_to_vietnamese(
                    int(self.move_id.amount_total)
                ).capitalize()+ " đồng"
            ),
            "OriginalInvoiceDetail": original_invoice_detail,
            "TaxRateInfo": [
                {
                    "VATRateName": "",  
                    "AmountWithoutVATOC": self.move_id.amount_untaxed or 0.0,
                    "VATAmountOC": self.move_id.amount_tax or 0.0
                }
            ]
        }
        if self.move_id.origin_move_id or self.move_id.reversed_entry_id:
            origin_move_id = self.move_id.origin_move_id or self.move_id.reversed_entry_id
            data.update({
                "OrgInvoiceType": 3,
                "ReferenceType": self._get_reference_type(),
                "OrgInvTemplateNo": origin_move_id.misa_template_id.inv_series[0] if origin_move_id else "",
                "OrgInvSeries": origin_move_id.misa_template_id.inv_series[1:] if origin_move_id else "",
                "OrgInvNo": origin_move_id.misa_inv_no or "",
                "OrgInvDate": datetime.datetime.now().strftime("%Y-%m-%d"),
                "OrgInveNote": self.move_id.ref or ""
            })
        return data
    
    def _get_reference_type(self):
        if self.move_id.origin_move_id and self.move_id.move_type == "out_invoice":
            return 1 # Hóa đơn thay thế
        elif self.move_id.reversed_entry_id and self.move_id.move_type == "out_refund":
            return 2 # Hóa đơn điểu chỉnh giảm
        else:
            return ""
    
    def action_save_as_draft(self):
        self._update_company_info()
        self.move_id.write({
            "misa_template_id": self.misa_template_id.id,
        })
    
    
    def _update_company_info(self):
        self.partner_id.company_name = self.customer_company_name
        self.partner_id.vat = self.customer_company_tax_code
        self.partner_id.street = self.customer_company_address
        self.partner_id.email = self.customer_email
    
    def _handle_publish_invoice_response(self, response):
        is_success = response.get("success")
        error_code = response.get("errorCode")
        invoice_error_code = None
        invoice_data = {}
        
        if is_success:
            result = response.get("createInvoiceResult") or response.get("publishInvoiceResult")
            invoice_data = json.loads(result)[0] if result else {}
            invoice_error_code = invoice_data.get("ErrorCode")
        
        return is_success, error_code, invoice_error_code, invoice_data
        
    def _get_misa_token(self, get_new=False):
        if not self.place_id:
                raise UserError(_("Place is not set. Cannot retrieve MISA token."))
        if get_new:
                return self.place_id._get_new_token()
        else:
                return self.place_id.auth_token or self.place_id._get_new_token()
