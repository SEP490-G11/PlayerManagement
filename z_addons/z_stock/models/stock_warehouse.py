# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ZStockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    place_id = fields.Many2one(
        "z_place.place",
        string="Cơ sở",
        required=True,
        tracking=True,
        help="Cơ sở mà kho hàng này thuộc về"
    )

    @api.constrains("place_id")
    def _check_place_id(self):
        """Kiểm tra ràng buộc cho place_id"""
        for record in self:
            if not record.place_id:
                raise ValidationError(_("Cơ sở là bắt buộc cho kho hàng."))

    @api.onchange("place_id")
    def _onchange_place_id(self):
        """Xử lý khi thay đổi cơ sở"""
        if self.place_id:
            # Có thể thêm logic xử lý khi thay đổi cơ sở
            pass

    def get_warehouses_by_place(self, place_id):
        """Lấy danh sách kho hàng theo cơ sở"""
        return self.search([("place_id", "=", place_id)])

    def get_warehouse_by_place_and_type(self, place_id, warehouse_type=None):
        """Lấy kho hàng theo cơ sở và loại (nếu có)"""
        domain = [("place_id", "=", place_id)]
        if warehouse_type:
            domain.append(("warehouse_type", "=", warehouse_type))
        return self.search(domain, limit=1)
