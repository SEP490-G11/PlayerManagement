from odoo import api, fields, models, tools, _


class ZProduct(models.Model):
    _inherit = "product.product"

    combo_id = fields.Many2one(
        "z_combo.combo", string="Combo", ondelete="cascade", index=True, copy=False
    )

    is_combo = fields.Boolean("Is combo", default=False)

    _sql_constraints = [
        (
            "combo_id_unique",
            "UNIQUE(combo_id)",
            "Each combo can only be assigned to one product.",
        ),
    ]
