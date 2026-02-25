from odoo import api, fields, models, _


class ZAccountComboLine(models.Model):
    _name = "account.combo.line"
    _description = "combo"

    combo_id = fields.Many2one("z_combo.combo", string="Combo", required=True)
    account_move_id = fields.Many2one(
        "account.move", string="invoice", ondelete="cascade"
    )
    _sql_constraints = [
        (
            "combo_product_unique",
            "unique(product_id, combo_id)",
            "Each product can only be assigned to a combo once.",
        ),
    ]
