from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.z_invoice.helpers.misa_utils import ZMISAUtils
import re

class ZPlace(models.Model):
    _name = "z_place.place"
    _inherit = ["z_place.place", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Branch Name", required=True, size=256, tracking=True)
    company_name_id = fields.Char(string="Company Name for VAT Invoice", size=256, tracking=True)
    tax_id = fields.Char(string="Company Tax ID for VAT Invoice", size=50, tracking=True)
    address_company = fields.Char(string="Company Address for VAT Invoice", size=256, tracking=True)
    appid = fields.Char(string="Invoice Software App ID", required=True, size=256, tracking=True)
    email_company = fields.Char(string="Login Email for Invoice Software", required=True, size=256, tracking=True)
    password = fields.Char(string="Password for Invoice Software", required=True, size=50, tracking=True)
    invoice_serial_number = fields.Char(string="VAT Invoice Serial Number", required=True, size=50, tracking=True)
    digital_signature_method = fields.Char(string="Digital Signature Method", default="HSM", required=True, tracking=True)
    auth_token = fields.Char(string="Auth Token")
    note = fields.Text(string="Notes", tracking=True, size=500)

    def _get_new_token(self):
        """
        Call the MISA API to obtain a new authentication token.
        """
        try: 
            response = ZMISAUtils.call_token_api(self.appid, self.tax_id, self.email_company, self.password, self.env)

            if response.get("success") and response.get("data"):
                result = response.get("data")
                if result and result.get("data"):
                    # Lưu token mới vào database
                    self.auth_token = result.get("data")
                    return self.auth_token
                else:
                    raise UserError(_("No token returned from MISA API"))
            else:
                raise UserError(response.get("errors") or _("API call failed"))
                
        except Exception as e:
            raise UserError(_("Error getting new MISA token"))


    @api.constrains('company_name_id', 'tax_id', 'address_company')
    def _check_conditional_required(self):
        for rec in self:
            filled = [bool(rec.company_name_id), bool(rec.tax_id), bool(rec.address_company)]
            if any(filled) and not all(filled):
                raise ValidationError(_(
                    "If one of Company Name, Tax ID, or Company Address is filled, all three must be filled!"
                ))

    @api.constrains('email_company')
    def _check_email(self):
        for rec in self:
            if rec.email_company and not re.match(r"[^@]+@[^@]+\.[^@]+", rec.email_company):
                raise ValidationError(_("Login Email for Invoice Software must be a valid email address."))

    @api.constrains('name', 'company_name_id', 'tax_id', 'address_company', 'appid', 'email_company', 'password', 'invoice_serial_number', 'digital_signature_method', 'note')
    def _check_field_lengths(self):
        for rec in self:
            if rec.name and len(rec.name) > 256:
                raise ValidationError(_("Branch Name: max 256 characters."))
            if rec.company_name_id and len(rec.company_name_id) > 256:
                raise ValidationError(_("Company Name for VAT Invoice: max 256 characters."))
            if rec.tax_id and len(rec.tax_id) > 50:
                raise ValidationError(_("Company Tax ID for VAT Invoice: max 50 characters."))
            if rec.address_company and len(rec.address_company) > 256:
                raise ValidationError(_("Company Address for VAT Invoice: max 256 characters."))
            if rec.appid and len(rec.appid) > 256:
                raise ValidationError(_("Invoice Software App ID: max 256 characters."))
            if rec.email_company and len(rec.email_company) > 256:
                raise ValidationError(_("Login Email for Invoice Software: max 256 characters."))
            if rec.password and len(rec.password) > 50:
                raise ValidationError(_("Password for Invoice Software: max 50 characters."))
            if rec.invoice_serial_number and len(rec.invoice_serial_number) > 50:
                raise ValidationError(_("VAT Invoice Serial Number: max 50 characters."))
            if rec.note and len(rec.note) > 500:
                raise ValidationError(_("Notes: max 500 characters."))

    def unlink(self):
        for rec in self:
            # Check for related data (example: employees, schedules, appointments, etc.)
            related_models = [
                ('hr.employee', 'place_id'),
                ('z_appointment.appointment', 'place_id'),
                # Add other related models and fields as needed
            ]
            for model, field in related_models:
                count = self.env[model].search_count([(field, '=', rec.id)])
                if count > 0:
                    raise ValidationError(_("Cannot delete branch with related data (e.g. employees, appointments, etc.)."))
        return super(ZPlace, self).unlink()   
