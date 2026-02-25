from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ZStockmove(models.Model):
    _inherit = "stock.move"

    product_uom_qty = fields.Float(
        digits="Stock_Product",
    )
    quantity = fields.Float(
        digits="Stock_Product",
    )
