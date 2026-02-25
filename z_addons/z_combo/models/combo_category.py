from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ZComboCategory(models.Model):
    _name = "z_combo.combo.category"
    _description = "Combo category"

    name = fields.Char("Category name", required=True)
    combo_count = fields.Integer(
        "# Combos",
        compute="_compute_z_combo_count",
        help="The number of combos under this category",
    )

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            if len(self.search([("name", "=", rec.name)])) > 1:
                raise ValidationError(_("Category name must be unique"))

    def _compute_z_combo_count(self):
        read_group_res = self.env["z_combo.combo"]._read_group(
            [("categ_id", "in", self.ids)], ["categ_id"], ["__count"]
        )
        group_data = {categ.id: count for categ, count in read_group_res}
        for categ in self:
            combo_count = 0
            for sub_categ_id in categ.search([("id", "=", categ.ids)]).ids:
                combo_count += group_data.get(sub_categ_id, 0)
            categ.combo_count = combo_count

    def unlink(self):
        for rec in self:
            combo = self.env["z_combo.combo"].search(
                [("category_id", "=", rec.id)], limit=1
            )
            if combo:
                raise ValidationError(
                    _("This category is having one or more combos depend on")
                )
            else:
                return super().unlink()
