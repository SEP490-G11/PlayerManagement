# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ZCls(models.Model):
    _name = "z_ophthalmology.cls"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Cls"

    name = fields.Char("Cls Name", required=True, tracking=True)
    price = fields.Float("Price", required=True, digits=(12, 0), default=0 )
    
    product_id = fields.Many2one(
        "product.product",
        string="Related Product",
        domain=[("is_glass_order", "=", True)],
    )
    
    def create(self, vals):
        if vals["price"] < 0:
            raise ValidationError(_("Price cls  is must be positive"))
        if len(self.search([("name", "=", vals["name"])])) > 1: 
            raise ValidationError(_("Price cls  is must be positive"))
        new_cls = super(ZCls, self).create(vals)
        category_id = (
            self.env["product.category"].search([("name", "=", "CLS")], limit=1).id
        )
        product_vals = {
            "name": (_("CLS") + f" {new_cls.name}"),
            "lst_price": new_cls.price,
            "detailed_type": "service",
            "categ_id": category_id,
            "cls_id": new_cls.id,
            "is_cls": True,
        }
        new_product = self.env["product.product"].create(product_vals)
        new_cls.product_id = new_product.id
        return new_cls
    
    def write(self, vals):
        data = {}
        if  vals.get("name"):
            data["name"] = (_("CLS") + f" {vals['name']}")
        if  vals.get("price"):
            data["lst_price"] =  vals["price"]
        self.product_id.write(data)
        return super().write(vals)
    
    def unlink(self):
        raise ValidationError(_("Can not delete CLS"))
        

    _sql_constraints = [
        (
            "unique_name",
            "unique(name)",
            _("Name must be unique"),
        ),
    ]
