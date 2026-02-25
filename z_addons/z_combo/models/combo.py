# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ZCombo(models.Model):
    _name = "z_combo.combo"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Combo"

    attach_combo_ids = fields.Many2many(
        "z_combo.combo",
        "z_combo_combo_rel",  # Tên bảng trung gian
        "combo_id",  # Tên cột đại diện cho bản ghi hiện tại
        "attached_combo_id",  # Tên cột đại diện cho bản ghi được liên kết
        string="Attached Combos",
    )

    @api.constrains("attach_combo_ids")
    def _check_category_recursion(self):
        for rec in self.attach_combo_ids:
            if rec.attach_combo_ids:
                raise ValidationError(
                    _(f"You cannot attach {rec.name} which have components combo.")
                )

    @api.model
    def _get_default_category_id(self):
        category_model = self.env["z_combo.combo.category"]
        categories = category_model.search([])
        return categories

    def _read_group_category_id(self, categories, domain, order):
        category_ids = self.env.context.get("default_category_id")
        if not category_ids and self.env.context.get("group_expand"):
            category_ids = categories._search(
                [], order=order, access_rights_uid=SUPERUSER_ID
            )
        return categories.browse(category_ids)

    code = fields.Char(string="Combo code", required=True)
    name = fields.Char(string="Combo name", required=True)
    category_id = fields.Many2one(
        "z_combo.combo.category",
        string="Category",
        change_default=True,
        default=_get_default_category_id,
        group_expand="_read_group_category_id",
        required=True,
    )
    combo_line_ids = fields.One2many(
        "z_combo.combo.line", "combo_id", string="Products in combo", copy=True
    )
    product_id = fields.Many2one(
        "product.product", string="Related product", domain=[("is_combo", "=", True)]
    )
    account_move_id = fields.Many2one(
        "account.move", ondelete="cascade", index=True, copy=False
    )

    num_of_products = fields.Integer(
        string="Number of products", compute="_compute_num_of_products"
    )
    validity_days = fields.Integer(string="Validity days", required=True, default=1)
    discount = fields.Integer(string="Discount", default=0)
    amount = fields.Integer(string="Amount", compute="_compute_amount", store=True)
    amount_without_discount = fields.Integer(
        string="Amount without discount", compute="_compute_amount_no_disc"
    )
    discount_on_products = fields.Float(
        "Discount on product", compute="_compute_discount_on_product"
    )
    amount_after_discount_on_products = fields.Float(
        "Amount after discount on product",
        compute="_compute_amount_after_discount_on_product",
    )
    discount_all_percent = fields.Float("Discount on all products", default=0)
    is_created = fields.Boolean("Is created" , default=False)

    @api.constrains("code", "name")
    def _check_length(self):
        for rec in self:
            if rec.code and len(rec.code) > 3:
                raise ValidationError(_("Code must be at most 3 characters."))
            if rec.name and len(rec.name) > 100:
                raise ValidationError(_("Name must be at most 100 characters."))
            if len(self.search([("name", "=", rec.name)])) > 1:
                raise ValidationError(_("Combo name must be unique"))
            if len(self.search([("code", "=", rec.code)])) > 1:
                raise ValidationError(_("Combo code must be unique"))

    @api.depends("combo_line_ids")
    def _compute_discount_on_product(self):
        for rec in self:
            discount_on_products = 0
            for line in rec.combo_line_ids:
                discount_on_products += line.discounts
            rec.discount_on_products = discount_on_products

    @api.depends("combo_line_ids")
    def _compute_amount_after_discount_on_product(self):
        for rec in self:
            rec.amount_after_discount_on_products = (
                rec.amount_without_discount - rec.discount_on_products
            )

    @api.constrains("discount_all_percent")
    def _check_name(self):
        for rec in self:
            if rec.discount_all_percent > 100 or rec.discount_all_percent < 0:
                raise ValidationError(
                    _("Discount on all products must be between 0 and 100.")
                )

    @api.constrains("discount_all_percent")
    def _check_validity_days(self):
        for record in self:
            if record.validity_days <= 0:
                raise ValidationError(_("Validity days must be greater than 0."))

    @api.constrains("discount")
    def _check_discount(self):
        for record in self:
            if record.discount < 0:
                raise ValidationError(_("Discount days must be greater than 0."))

    @api.constrains("combo_line_ids")
    def _check_num_of_products(self):
        for record in self:
            if not record.combo_line_ids:
                raise ValidationError(
                    _("Combo must consist of at least 1 product/drug/service.")
                )

    @api.depends("combo_line_ids")
    def _compute_amount_no_disc(self):
        for rec in self:
            total = sum(line.price * line.quantity for line in rec.combo_line_ids)
            rec.amount_without_discount = total

    @api.depends("combo_line_ids", "discount_all_percent")
    def _compute_amount(self):
        for rec in self:
            rec.amount = (
                rec.amount_after_discount_on_products
                * (100 - rec.discount_all_percent)
                / 100
            )

    @api.depends("combo_line_ids")
    def _compute_num_of_products(self):
        for rec in self:
            rec.num_of_products = len(rec.combo_line_ids)

    @api.model
    def create(self, vals):
        vals["is_created"] = True
        new_combo = super(ZCombo, self).create(vals)
        return new_combo
    
    # TODO: re-review old logic

    # @api.model
    # def create(self, vals):
    #     new_combo = super(ZCombo, self).create(vals)
    #     category_id = (
    #         self.env["product.category"].search([("name", "=", "All")], limit=1).id
    #     )
    #     product_vals = {
    #         "name": new_combo.name,
    #         "list_price": new_combo.amount,
    #         "combo_id": new_combo.id,
    #         "detailed_type": "product",
    #         "categ_id": category_id,
    #         "is_combo": True,
    #     }
    #     new_combo.product_id = self.env["product.product"].create(product_vals).id
    #     return new_combo
    #
    # def write(self, vals):
    #     result = super(ZCombo, self).write(vals)
    #     for combo in self:
    #         product_vals = {}
    #         if "name" in vals:
    #             product_vals["name"] = combo.name
    #         product_vals["list_price"] = combo.amount
    #         if product_vals:
    #             combo.product_id.write(product_vals)
    #     return result
    #
    # def unlink(self):
    #     product_ids_to_remove = self.mapped("product_id.id")
    #     result = super(ZCombo, self).unlink()
    #     if product_ids_to_remove:
    #         product = self.env["product.template"].browse(product_ids_to_remove)
    #         product.unlink()
    #     return result

    @api.onchange("attach_combo_ids")
    def on_change_attach_combo_ids(self):
        # Xóa các dòng trong combo_line_ids nếu không còn trong attach_combo_ids
        attach_combo_ids = self.attach_combo_ids.mapped(
            "id"
        )  # Lấy danh sách ID của attach_combo_ids
        self.combo_line_ids = self.combo_line_ids.filtered(
            lambda x: x.sub_combo_id in attach_combo_ids or not x.sub_combo_id
        )

        new_products = self.env["z_combo.combo.line"]
        for rec in self.attach_combo_ids:
            parent_id = rec._origin.id
            for line in rec.combo_line_ids:
                new_line = new_products.create(
                    {
                        "product_id": line.product_id.id,
                        "quantity": line.quantity,
                        "price": line.price,
                        "discounts": line.discounts,
                        "sub_combo_id": parent_id,
                        "combo_id": self.id,
                    }
                )
                new_products |= new_line
        self.combo_line_ids |= new_products
