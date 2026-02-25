from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
from odoo.addons.z_invoice.helpers.utils import ZInvoiceUtils   
from odoo.addons.z_invoice.helpers.misa_utils import ZMISAUtils

_logger = logging.getLogger(__name__)

class ZMISAInvoiceTemplate(models.Model):
    _name = "z_invoice.misa_invoice_template"
    _description = "MISA Invoice Template"
    _order = "create_date desc"

    name = fields.Char(string="Name")
    template_id = fields.Char(string="Template ID")
    template_name = fields.Char(string="Template Name")
    inv_series = fields.Char(string="Inv Series")
    inactive = fields.Boolean(string="Inactive", default=False)
    is_inherit_from_old_template = fields.Boolean(string="Is Inherit From Old Template", default=False)
    is_send_summary = fields.Boolean(string="Is Send Summary", default=False)
    is_petrol = fields.Boolean(string="Is Petrol", default=False)
    is_more_vat_rate = fields.Boolean(string="Is More VAT Rate", default=False)
    template_content = fields.Text(string="Template Content")
    is_default = fields.Boolean(string="Is Default", default=False)
    
    
    def action_create_misa_template(self):
        token = self.env['ir.config_parameter'].sudo().get_param('misa.api.token')
        result = ZMISAUtils.call_invoice_templates_api(token)
        if result.get('success'):
            templates = result['data'].get('data', [])
            for tmpl in templates:
                self.create({
                    'name': tmpl.get('TemplateName'),
                    'template_id': tmpl.get('IPTemplateID'),
                    'template_name': tmpl.get('TemplateName'),
                    'inv_series': tmpl.get('InvSeries'),
                    'inactive': tmpl.get('Inactive', False),
                    'is_inherit_from_old_template': tmpl.get('IsInheritFromOldTemplate', False),
                    'is_send_summary': tmpl.get('IsSendSummary', False),
                    'is_petrol': tmpl.get('IsPetrol', False) if tmpl.get('IsPetrol') is not None else False,
                    'is_more_vat_rate': tmpl.get('IsMoreVATRate', False),
                    'template_content': tmpl.get('TemplateContent'),
                    'is_default': tmpl.get('IsDefault', False),
                })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }