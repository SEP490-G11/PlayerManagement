# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class ZAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # price_unit = fields.Float(
    #     string="Unit price",
    #     compute="_compute_price_unit",
    #     store=True,
    #     readonly=False,
    #     precompute=True,
    #     digits=(12, 0),
    # )
    discount_amount = fields.Float(
        string="Discount Amount", digits=(12, 0), default=0.0
    )
    # discount = fields.Float(
    #     string="Discount", digits=(12, 9), compute="_compute_discount", store=False
    # )
    # assign new field for discount in invoice
    discount_invoice = fields.Float(
        string="Discount invoice", digits=(12, 9), compute="_compute_discount_invoice", store=False
    )
    discount = fields.Float(
        string='Discount (%)',
        compute=False,
        store=True,
        digits='Discount',
        default=0.0,
    )
    discount_amount_line = fields.Float(
        string="Discount Amount Line", 
        digits=(12, 0), 
        compute="_compute_discount_amount_line", 
        store=True
    )

    is_promotion_line = fields.Boolean(
        string="Is Promotion Line",
        help="This line is a promotion line, not a real product",
        compute="_compute_is_promotion_line",
        store=False,
        default=False,
    )
    total_without_discount = fields.Float(
        string="Total without discount", compute="_compute_total_without_discount"
    )
    # quantity = fields.Float(
    #     string="Quantity",
    #     compute="_compute_quantity",
    #     store=True,
    #     readonly=False,
    #     precompute=True,
    #     digits=(12, 0),
    #     help="The optional quantity expressed by this line, eg: number of product sold. "
    #     "The quantity is not a legal requirement but is very useful for some reports.",
    #     widget="integer",
    # )
    amount_residual = fields.Float(digits="Invoice")
    price_subtotal = fields.Monetary(digits="Invoice")
    price_total = fields.Monetary(digits="Invoice")
    combo_id = fields.Many2one("z_combo.combo", string="Combo")
    total_after_discount_combo_line = fields.Float(
        string="Tổng thanh toán combo",
        compute="compute_total_after_discount_combo_line",
        store=True,
    )
    total_after_discount_combo_line_paid = fields.Float(
        string="Tổng doanh thu combo",
        compute="_compute_total_after_discount_combo_line_paid",
        store=True,
    )

    @api.depends(
        "quantity",
        "price_unit",
        "discount_amount",
        "combo_id",
    )
    def compute_total_after_discount_combo_line(self):
        for rec in self:
            total_discount = 0
            total_without_discount = 0
            if rec.combo_id:
                if rec.discount_amount:
                    total_discount = rec.discount_amount
                if rec.quantity and rec.price_unit:
                    total_without_discount = rec.quantity * rec.price_unit
            rec.total_after_discount_combo_line = (
                total_without_discount - total_discount
            )

    @api.depends(
        "quantity",
        "price_unit",
        "discount_amount",
        "combo_id",
        "move_id",
        "move_id.state",
        "move_id.payment_state",
    )
    def _compute_total_after_discount_combo_line_paid(self):
        for rec in self:
            if rec.move_id.state == "posted" and rec.move_id.payment_state == "paid":
                total_discount = 0
                total_without_discount = 0
                if rec.combo_id:
                    if rec.discount_amount:
                        total_discount = rec.discount_amount
                    if rec.quantity and rec.price_unit:
                        total_without_discount = rec.quantity * rec.price_unit
                rec.total_after_discount_combo_line_paid = (
                    total_without_discount - total_discount
                )
            else:
                rec.total_after_discount_combo_line_paid = 0

    product_category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        related="product_id.categ_id",
    )

    @api.depends("quantity", "discount_amount", "price_unit")
    def _compute_discount_invoice(self):
        pass

    @api.depends("discount_amount")
    def _compute_total_discount(self):
        total_discount_amount = 0
        for line in self:
            total_discount_amount += line.discount_amount
        self.total_discount_amount = total_discount_amount

    @api.depends("quantity", "price_unit")
    def _compute_total_without_discount(self):
        total = 0
        for line in self:
            total += line.quantity * line.price_unit
        self.total_without_discount = total

    def has_duplicates(self):
        seen = set()
        for item in self:
            if item.product_id.id in seen:
                return True
            seen.add(item.product_id.id)
        return False

    @api.onchange("discount_amount")
    def onchange_discount_amonnt(self):
        for line in self:
            if line.discount_amount > line.total_without_discount:
                raise ValidationError(_("Discount amount is greater than total amount"))
            if line.discount_amount < 0:                
                raise ValidationError(_("Discount amount cannot be negative"))
            
    @api.depends("price_unit", "price_total")
    def _compute_is_promotion_line(self):
        for line in self:
            # Check if the product is a promotion product
            if line.price_unit <= 0 and line.price_total <= 0:
                line.is_promotion_line = True
            else:
                line.is_promotion_line = False

    @api.depends("quantity", "price_unit", "discount")
    def _compute_discount_amount_line(self):
        for line in self:
            line.discount_amount_line = (
                0
                if line.discount == 0 or line.quantity == 0 or line.price_unit == 0 or (line.price_unit < 0 and line.price_total < 0)
                else
                (line.quantity * line.price_unit * (line.discount / 100.0))
            )
