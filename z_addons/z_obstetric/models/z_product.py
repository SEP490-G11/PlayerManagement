from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ZProductTemplate(models.Model):
    _inherit = "product.template"

    detailed_type = fields.Selection(
        [
            ("consu", _("Consu")),
            ("service", _("Service")),
            ("product", _("Product")),
        ],
        string="Product Type",
    )
    product_tooltip = fields.Text(
        default=lambda self: _("Default Product Tooltip"), readonly=True
    )
    service_code = fields.Many2one(string="Service Code", comodel_name="service.code")
    service_name = fields.Char(related="service_code.service_name", store=True)

    pharmacological = fields.Char(string="Pharmacological group classification")
    fn_material = fields.Char(string="Full name of the material")
    brand_trade = fields.Char(string="Brand name/Trade name")
    concentration_content_specifications = fields.Char(
        string="Concentration/Content/Specifications"
    )
    preparation = fields.Char(string="Preparation/Specifications 2")
    route_admin = fields.Char(string="Route of administration/Specifications")

    @api.constrains("detailed_type", "service_code")
    def _check_service_product(self):
        for record in self:
            if record.detailed_type != "service" and record.service_code:
                raise ValidationError(
                    _("Do not use reference codes for consumables and stock items.")
                )
