# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ZService(models.Model):
    _name = "z_medical_record.service"
    _description = "Product Service"

    product_id = fields.Many2one(
        "product.product", string="Product", domain="[('detailed_type','=', 'service')]",required=True
    )  # Dịch vụ
    sequence = fields.Integer("Sequence")
    name = fields.Char("Name", related="product_id.name")  # Tên
    quantity = fields.Integer("Quantity")  # Số lượng
    unit = fields.Char("Unit")  # Đơn vị
