from odoo import fields, models
from odoo.exceptions import ValidationError


class ZIframe(models.TransientModel):
    _name = "z_web.iframe"
    _description = "Iframe"
    
    url = fields.Text("Url Iframe")
    