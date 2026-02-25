from odoo import api, fields, models, _


class ZGlassOrderLine(models.Model):
    _name = "z_glass_order.line"
    _description = "Glass Order Items"

    product_id = fields.Many2one("product.product", string="Product", required=True)
    glass_order_id = fields.Many2one("z_glass_order", ondelete="cascade", required=True)
    price = fields.Float("Price", related="product_id.list_price")
    quantity = fields.Integer("Quantity", default=1)
    amount = fields.Integer("Amount", compute="_compute_amount", store=True)

    _sql_constraints = [
        (
            "glass_order_product_unique",
            "unique(product_id, glass_order_id)",
            "Each product can only be assigned to a glass order once.",
        ),
    ]

    @api.depends("quantity", "price")
    def _compute_amount(self):
        for record in self:
            record.amount = record.quantity * record.price
