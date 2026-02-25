# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    place_id = fields.Many2one("z_place.place", string="Place")

    def _get_procurement_group(self):
        group = super()._get_procurement_group()
        
        if self.branch_id:
            wh = self.env["stock.warehouse"].search([
                ("place_id", "=", self.place_id.id)
            ], limit=1)
            if wh:
                group.warehouse_id = wh
        return group
    
    def action_confirm(self):
        if self.place_id not in self.user_id.place_ids:
            raise ValidationError(_("You are not allowed to confirm this sale order in other branch."))
        
        wh = self.env["stock.warehouse"].search([
            ("place_id", "=", self.place_id.id)
        ], limit=1)
        if wh:
            self.warehouse_id = wh.id
        
        return super().action_confirm()