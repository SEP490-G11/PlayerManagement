from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ZComboLine(models.Model):
    _name = "z_combo.combo.line"
    _description = "Product Combo Items"

    product_id = fields.Many2one("product.product", string="Product", required=True)
    combo_id = fields.Many2one("z_combo.combo", ondelete="cascade")
    price = fields.Float("Price", related="product_id.list_price")
    quantity = fields.Integer("Quantity")
    discounts = fields.Float("Discounts", default=0.0, digits=(12, 0))
    price_after_discount = fields.Float(
        "Price After Discount", compute="_compute_price_after_discount", store=True
    )
    amount = fields.Integer("Amount", compute="_compute_amount", store=True)
    sub_combo_id = fields.Many2one("z_combo.combo", string="Combo")
    is_sub_combo = fields.Boolean("Is Sub Combo", default=False)
    discount_percent = fields.Float(
        "Discount (%)", compute="compute_discount_percent", store=True
    )

    @api.depends("combo_id.discount_all_percent")
    def compute_discount_percent(self):
        for rec in self:
            rec.discount_percent = rec.combo_id.discount_all_percent or 0.0

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_("Quantity must be greater than 0."))

    @api.constrains("discounts")
    def _check_dis(self):
        for record in self:
            if record.discounts < 0:
                raise ValidationError(
                    _("Discounts must be greater than or equal to 0.")
                )

    @api.depends("quantity", "price_after_discount")
    def _compute_amount(self):
        for record in self:
            record.amount = (
                (record.price * record.quantity - record.discounts)
                * (100 - record.discount_percent)
                / 100
            )

    @api.depends("price", "discounts", "discount_percent", "quantity")
    def _compute_price_after_discount(self):
        for record in self:
            discount_on_product = 0
            if record.quantity:
                discount_on_product = record.discounts / record.quantity

            record.price_after_discount = (
                (record.price - discount_on_product)
                * (100 - record.discount_percent)
                / 100
            )

    _sql_constraints = []
