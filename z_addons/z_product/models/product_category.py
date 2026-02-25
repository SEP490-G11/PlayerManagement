from odoo import fields, models, _, api, exceptions, tools


class ProductCategory(models.Model):
    _inherit = "product.category"

    categ_code = fields.Char(string="Category Code")
