# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class ZAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_glass_order = fields.Boolean("Is glass Order", related="product_id.is_glass_order")
    
    # def unlink(self):
    #     for record in self:
    #          if record.product_id.is_glass_order: 
    #             glass_order = self.env["z_glass_order"].search([("product_id",'=',record.product_id.id)], limit = 1)
    #             glass_order.is_added = False
    #     return super().unlink()
