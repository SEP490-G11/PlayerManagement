# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class ZSaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("z_appointment_id")
    def _onchange_z_appointment_id(self):
        new_products = self.env["sale.order.line"]
        product_quantities = {}

        models_to_search = [
            self.env["z_ophthalmology.comprehensive"],
            self.env["z_ophthalmology.lens"],
            self.env["z_ophthalmology.re_lens"],
            self.env["z_ophthalmology.vision"],
            self.env["z_ophthalmology.binocular_vision"],
        ]

        # Search for related records in the specified models
        for model in models_to_search:
            record = model.search(
                [("visit_id", "=", self.z_appointment_id.id)], limit=1
            )
            if record:
                for order in record.drug_ids:
                    if order.product_id.id in product_quantities:
                        product_quantities[order.product_id.id] += order.quantity
                    else:
                        product_quantities[order.product_id.id] = order.quantity
                for cls in record.cls_ids:
                    if cls.id in product_quantities:
                        product_quantities[cls.id] += 1
                    else:
                        product_quantities[cls.id] = 1
                    

        # Search for glass orders related to the current partner
        glass_orders = self.env["z_glass_order"].search(
            [("visit_id", "=", self.z_appointment_id.id), ("is_added", "=", False)]
        )

        # Add glass orders to the product quantities
        for order in glass_orders:
            order_code = order.code
            for line in order.glass_order_line_ids:
                # if line.product_id.id in product_quantities:
                #     product_quantities[line.product_id.id] += line.quantity
                # else:
                #     product_quantities[line.product_id.id] = line.quantity
                line_data = {
                    "product_id": line.product_id.id,
                    'name': order_code,
                    "product_uom_qty": line.quantity,
                }
                new_line = new_products.new(line_data)
                new_products += new_line
                
        # Create new lines from the accumulated product quantities
        for product_id, quantity in product_quantities.items():
            line_data = {
                "product_id": product_id,
                "product_uom_qty": quantity,
            }
            new_line = new_products.new(line_data)
            new_products += new_line

        self.order_line = new_products
