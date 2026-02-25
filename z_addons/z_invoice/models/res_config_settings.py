from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    misa_api_url = fields.Char(
        string="MISA API URL",
        config_parameter='z_invoice.misa_api_url',
        default="https://testapi.meinvoice.vn/api/integration",
        help="Base URL for MISA API integration"
    )
    misa_api_timeout = fields.Integer(
        string="MISA API Timeout (seconds)",
        config_parameter='z_invoice.misa_api_timeout',
        default=30,
        help="Timeout for MISA API calls in seconds"
    ) 