# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class ZAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_method = fields.Selection(
        [
            ("percentage", ("%")),
            ("fixed", ("VND")),
        ],
        default="fixed",
        string="Discount Method",
    )

    @api.onchange("discount_method")
    def _onchange_discount_method_after_sale(self):
        self.discount_amount = 0

    @api.onchange("discount_amount", "discount_method")
    def onchange_discount_amonnt(self):
        for line in self:
            if line.discount_method == "fixed":
                if line.discount_amount > line.total_without_discount:
                    raise ValidationError(
                        _("Discout amount is greater than total amount")
                    )
            if line.discount_method == "percentage":
                if line.discount_amount > 100:
                    raise ValidationError(
                        _("Discout amount is greater than total amount")
                    )

    @api.depends("quantity", "discount_amount", "price_unit", "discount_method")
    def _compute_discount(self):
        for line in self:
            discount = 0
            if line.discount_method == "fixed":
                discount = (
                    0
                    if line.price_unit == 0 or line.quantity == 0
                    else (line.discount_amount / (line.price_unit * line.quantity))
                    * 100.0
                )
            if line.discount_method == "percentage":
                discount = line.discount_amount
            line.discount = discount

    @api.depends(
        "quantity",
        "discount",
        "price_unit",
        "tax_ids",
        "currency_id",
        "move_id",
        "move_id.discount_method_after_sale",
        "move_id.discount_after_sale",
    )
    def _compute_totals(self):
        for line in self:
            if line.display_type != "product":
                line.price_total = line.price_subtotal = False
            # Compute 'price_subtotal'.
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
            subtotal = line.quantity * line_discount_price_unit
            if (
                line.move_id.discount_method_after_sale == "percentage"
                and line.move_id.discount_after_sale
            ):
                subtotal = (line.quantity * line_discount_price_unit) * (
                    1 - line.move_id.discount_after_sale / 100
                )

            # Compute 'price_total'.
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res["total_excluded"]
                line.price_total = taxes_res["total_included"]
            else:
                line.price_total = line.price_subtotal = subtotal
