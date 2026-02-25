# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.fields import Command


class ZSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    combo_id = fields.Many2one("z_combo.combo", "Combo")
    sub_combo_id = fields.Many2one("z_combo.combo", "Sub Combo")

    def _prepare_invoice_line(self, **optional_values):

        self.ensure_one()
        res = {
            "display_type": self.display_type or "product",
            "sequence": self.sequence,
            "name": self.name,
            "product_id": self.product_id.id,
            "product_uom_id": self.product_uom.id,
            "quantity": self.qty_to_invoice,
            "discount": self.discount,
            "price_unit": self.price_unit,
            "tax_ids": [Command.set(self.tax_id.ids)],
            "sale_line_ids": [Command.link(self.id)],
            "is_downpayment": self.is_downpayment,
        }
        self._set_analytic_distribution(res, **optional_values)
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res["account_id"] = False
        if self.combo_id:
            res["combo_id"] = (self.combo_id.id,)
        if self.sub_combo_id:
            res["sub_combo_id"] = (self.sub_combo_id.id,)
        return res
