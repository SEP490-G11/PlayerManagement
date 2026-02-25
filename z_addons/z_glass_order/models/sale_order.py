from odoo import models, fields, api

class ZSaleOrder(models.Model):
    _inherit = 'sale.order'
    
    glass_order_id = fields.Many2one('z_glass_order', string='Glass Order')

    def write(self, vals):
        if "state" in vals:
            new_state = vals["state"]
            for record in self:
                glass_order = record.glass_order_id 
                if glass_order:
                    if new_state == "cancel":
                        glass_order.write({"is_added": False})
                        glass_order.sale_order_id = False
                    elif new_state in ['sent', 'sale']: 
                        glass_order.write({"is_added": True})
        sale_order_after = super(ZSaleOrder, self).write(vals)
        return sale_order_after