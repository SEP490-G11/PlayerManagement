from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ZProductTemplate(models.Model):
    _inherit = "product.template"

    quantity_per_day = fields.Integer(string="Quantity per day", required=False)
    ingredients = fields.Text(string="Ingredients", required=False)
    packaging = fields.Text(string="Packaging", required=False)
    instruction = fields.Text(string="Instruction", required=False)
    taxes_id = fields.Many2many(default=False)
    list_price = fields.Float(
        "Sales Price",
        default=1.0,
        digits=(12, 0),
        help="Price at which the product is sold to customers.",
    )
    standard_price = fields.Float(
        "Cost",
        compute="_compute_standard_price",
        inverse="_set_standard_price",
        search="_search_standard_price",
        digits=(12, 0),
        groups="base.group_user",
        help="""Value of the product (automatically computed in AVCO).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""",
    )
    vietmis_code = fields.Char(string="Vietmis Code")
    sell_help = fields.Boolean(string="Sell Help", default=False)

    def create(self, vals):
        if isinstance(vals, dict):
            for k, v in vals.items():
                if isinstance(v, str):
                    vals[k] = v.strip()
        elif isinstance(vals, list):
            for val in vals:
                if isinstance(val, dict):
                    for k, v in val.items():
                        if isinstance(v, str):
                            val[k] = v.strip()
        product = super(ZProductTemplate, self).create(vals)
        product.write({"taxes_id": [(5, 0, 0)]})
        return product

    def write(self, vals):
        if isinstance(vals, dict):
            for k, v in vals.items():
                if isinstance(v, str):
                    vals[k] = v.strip()
        elif isinstance(vals, list):
            for val in vals:
                if isinstance(val, dict):
                    for k, v in val.items():
                        if isinstance(v, str):
                            val[k] = v.strip()
        return super(ZProductTemplate, self).write(vals)

    @api.constrains("name")
    def _constrains_product_template_name(self):
        for rec in self:
            if len(self.search([("name", "=", rec.name)])) > 1:
                raise ValidationError(_("Product must be unique"))


class ZProductProduct(models.Model):
    _inherit = "product.product"
    lst_price = fields.Float(
        digits="Product",
    )
    standard_price = fields.Float(
        digits="Product",
    )

    @api.model
    def create(self, vals):
        if isinstance(vals, dict):
            for k, v in vals.items():
                if isinstance(v, str):
                    vals[k] = v.strip()
        elif isinstance(vals, list):
            for val in vals:
                if isinstance(val, dict):
                    for k, v in val.items():
                        if isinstance(v, str):
                            val[k] = v.strip()
        return super(ZProductProduct, self).create(vals)

    def write(self, vals):
        if isinstance(vals, dict):
            for k, v in vals.items():
                if isinstance(v, str):
                    vals[k] = v.strip()
        elif isinstance(vals, list):
            for val in vals:
                if isinstance(val, dict):
                    for k, v in val.items():
                        if isinstance(v, str):
                            val[k] = v.strip()
        return super(ZProductProduct, self).write(vals)

    # @api.constrains("name")
    # def _constrains_product_product_name(self):
    #     for rec in self:
    #         if len(self.search([("name", "=", rec.name)])) > 1:
    #             raise ValidationError(_("Product must be unique"))
