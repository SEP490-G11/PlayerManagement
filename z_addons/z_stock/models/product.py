from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ZProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available = fields.Float(
        digits="Stock_Product",
    )
    virtual_available = fields.Float(
        digits="Stock_Product",
    )

    usage_id = fields.Many2one(string="Usage", comodel_name="z.usage")

    supplier_ids = fields.Many2many(
        string="Suppliers", comodel_name="res.partner", compute="_compute_supplier_ids"
    )

    @api.depends()
    def _compute_supplier_ids(self):
        for rec in self:
            supplier_ids = []
            picking = self.env["stock.picking"].search(
                [("picking_code", "=", "incoming")]
            )
            if picking:
                for move in picking:
                    if rec.id in move.move_ids_without_package.mapped("product_id").ids:
                        supplier_ids.append(move.partner_id.id)
            rec.supplier_ids = [(6, 0, list(set(supplier_ids)))]


class ZProductProduct(models.Model):
    _inherit = "product.product"

    qty_available = fields.Float(
        digits="Stock_Product",
    )
    virtual_available = fields.Float(
        digits="Stock_Product",
    )

    supplier_ids = fields.Many2many(
        string="Suppliers", comodel_name="res.partner", compute="_compute_supplier_ids"
    )

    @api.depends()
    def _compute_supplier_ids(self):
        for rec in self:
            supplier_ids = []
            picking = self.env["stock.picking"].search(
                [("picking_code", "=", "incoming")]
            )
            if picking:
                for move in picking:
                    if rec.id in move.move_ids_without_package.mapped("product_id").ids:
                        supplier_ids.append(move.partner_id.id)
            rec.supplier_ids = [(6, 0, list(set(supplier_ids)))]
