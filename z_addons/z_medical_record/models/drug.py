# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ZDrug(models.Model):
    _name = "z_medical_record.drug"
    _description = "Drug"

    product_id = fields.Many2one(
        "product.product", string="Product", required=True
    )  # Thuốc
    sequence = fields.Integer("Sequence")
    name = fields.Char("Name", related="product_id.name")  # Tên thuốc
    quantity = fields.Integer("Quantity", default=1)  # Số lượng
    unit = fields.Char("Unit")  # Đơn vị
    usage = fields.Char("Usage")  # Cách dùng
    usage_id = fields.Many2one(string="Usage", comodel_name="z.usage")  # Cách dùng

    @api.onchange("product_id")
    def onchange_product_id(self):
        self.usage = (
            self.product_id.instruction if self.product_id.instruction else False
        )
        self.usage_id = self.product_id.usage_id if self.product_id.usage_id else False

        self.unit = self.product_id.uom_name if self.product_id.uom_name else False
