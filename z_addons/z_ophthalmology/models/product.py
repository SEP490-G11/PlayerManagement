from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError



class ZProduct(models.Model):
    _inherit = "product.product"

    is_cls = fields.Boolean("Is CLS", default=False,  compute='_compute_is_cls' , store=True)
    
    @api.depends('categ_id')
    def _compute_is_cls(self):
        for rec in self:
            rec.is_cls = "cls" in rec.categ_id.name.lower()
