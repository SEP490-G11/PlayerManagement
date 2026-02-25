from odoo import api, fields, models, tools, _


class ZProduct(models.Model):
    _inherit = "product.product"

    # glass_order_id = fields.Many2one(
    #     "z_glass_order",
    #     string="Glass Order",
    #     ondelete="cascade",
    #     index=True,
    #     copy=False,
    # )
    is_glass_order = fields.Boolean("Is Glass Order", default=False)

    # _sql_constraints = [
    #     (
    #         "glass_order_id_unique",
    #         "UNIQUE(glass_order_id)",
    #         "Each glass order can only be assigned to one product.",
    #     ),
    # ]
