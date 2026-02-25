# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from datetime import date


class ZAccountMove(models.Model):
    _inherit = "account.move"

    place_id = fields.Many2one(
        "z_place.place",
        string="Place",
        required=True,
        default=lambda self: self.get_default_place_id(),
    )

    invoice_type = fields.Selection(
        [
            ("all", "All"),
            ("service", "Service"),
            ("product", "Product"),
        ],
        string="Invoice Type",
        compute="_compute_invoice_type",
    )

    def get_default_place_id(self):
        place = self.env["z_place.place"].search([], limit=1)
        if place:
            return place.id
        return False

    @api.onchange("z_appointment_id")
    def _onchange_z_appointment_id_place(self):
        self.place_id = (
            self.z_appointment_id.place_id
            if self.z_appointment_id
            else self.get_default_place_id()
        )
        self.appointment_place = True if self.z_appointment_id else False

    def merge_duplicate_product_lines(self):
        if not self.env.context.get("linked_from_appointment"):
            line_ids = self.invoice_line_ids.filtered(lambda l: l.product_id)
            products = line_ids.mapped("product_id")
            for product in products:
                product_lines = line_ids.filtered(lambda l: l.product_id == product)
                if len(product_lines) > 1:
                    product_lines[0].quantity = sum(product_lines.mapped("quantity"))
                    self.invoice_line_ids = [(2, product_lines[1:].id, 0)]

    @api.onchange("z_appointment_id")
    def _onchange_z_appointment_id(self):
        new_products = self.env["account.move.line"]
        record = self.env["z_appointment.appointment"].browse(self.z_appointment_id.id)
        if record and not self.env.context.get("drug_order"):
            # Process medical tips lines
            for order_line in record.medical_tips_line_ids:
                new_line = new_products.new({"product_id": order_line.service_id.id})
                new_products += new_line

            # Process medical test lines
            for order_line in record.medical_test_line_ids:
                new_line = new_products.new({"product_id": order_line.service_id.id})
                new_products += new_line

            # Explicitly check each condition and add corresponding product
            if record.include_gynecological_form:
                product = self.env["product.product"].search(
                    [("service_name", "=", "PKH")], limit=1
                )
                if product:
                    new_line = new_products.new({"product_id": product.id})
                    new_products += new_line

            if record.include_non_speculum_gynecological_form:
                product = self.env["product.product"].search(
                    [("service_name", "=", "KMV")], limit=1
                )
                if product:
                    new_line = new_products.new({"product_id": product.id})
                    new_products += new_line

            if record.include_pre_first_trimester_pregnant_form:
                product = self.env["product.product"].search(
                    [("service_name", "=", "KTB")], limit=1
                )
                if product:
                    new_line = new_products.new({"product_id": product.id})
                    new_products += new_line

            if record.include_post_first_trimester_pregnant_form:
                product = self.env["product.product"].search(
                    [("service_name", "=", "KDB")], limit=1
                )
                if product:
                    new_line = new_products.new({"product_id": product.id})
                    new_products += new_line

            if record.include_full_body_examination_form:
                product = self.env["product.product"].search(
                    [("service_name", "=", "KTT")], limit=1
                )
                if product:
                    new_line = new_products.new({"product_id": product.id})
                    new_products += new_line

            if record.include_ovulation_indicated:
                product = self.env["product.product"].search(
                    [("service_name", "=", "KNN")], limit=1
                )
                if product:
                    new_line = new_products.new({"product_id": product.id})
                    new_products += new_line

            if record.include_pre_first_indicated:
                product = self.env["product.product"].search(
                    [("service_name", "=", "SDB")], limit=1
                )
                if product:
                    new_line = new_products.new({"product_id": product.id})
                    new_products += new_line

            if record.include_post_first_indicated:
                product = self.env["product.product"].search(
                    [("service_name", "=", "STB")], limit=1
                )
                if product:
                    new_line = new_products.new({"product_id": product.id})
                    new_products += new_line

            if record.include_gynecological_indicated:
                product = self.env["product.product"].search(
                    [("service_name", "=", "SAP")], limit=1
                )
                if product:
                    new_line = new_products.new({"product_id": product.id})
                    new_products += new_line
            
            if record.include_gynecological_form:
                product = self.env["product.product"].search(
                    [("service_name", "=", "S4D")], limit=1
                )
                if product:
                    new_line = new_products.new({"product_id": product.id})
                    new_products += new_line
                    
        if record and self.env.context.get("drug_order"):
            for order_line in record.general_result_ids[:1].product_drug_ids:
                new_line = new_products.new(
                    {
                        "product_id": order_line.product_id.id,
                        "quantity": order_line.quantity,
                        "currency_id": self.currency_id.id,
                    }
                )
                new_products += new_line

        self.invoice_line_ids = new_products

    discount_after_sale = fields.Float(
        string="Discount after sale",
        default=0,
        digits=(12, 0),
    )
    total_discount_after_sale_percentage = fields.Monetary(
        string="Total discount after sale percentage",
        default=0,
        digits=(12, 0),
        compute="_compute_total_discount_after_sale_percentage",
        store=True,
    )
    total_discount_all = fields.Monetary(
        string="Total discount all",
        default=0,
        digits=(12, 0),
        compute="_compute_total_discount_all",
        store=True,
    )

    discount_method_after_sale = fields.Selection(
        [("percentage", ("%"))],
        default="percentage",
        string="Discount method after sale",
        readonly=True,
    )
    place_id = fields.Many2one(required=False)

    total_discount_after_sale_by_product = fields.Monetary(
        string="Total discount after sale by product",
        default=0,
        digits=(12, 0),
        compute="_compute_total_discount_after_sale_by_product",
        store=True,
    )

    @api.depends(
        "invoice_line_ids",
        "invoice_line_ids.discount_amount",
        "invoice_line_ids.discount_method",
        "invoice_line_ids.price_unit",
        "invoice_line_ids.quantity",
    )
    def _compute_total_discount(self):
        for rec in self:
            total_discount = False
            for line in rec.invoice_line_ids:
                if line.discount_method == "percentage":
                    total_discount += (
                        line.quantity * line.discount_amount * line.price_unit / 100.0
                    )
                if line.discount_method == "fixed":
                    total_discount += line.discount_amount
            self.total_discount = total_discount

    @api.depends(
        "total_without_discount",
        "total_discount",
        "discount_after_sale",
        "discount_method_after_sale",
    )
    def _compute_total_after_discount(self):
        for rec in self:
            total_after_discount = 0
            if rec.discount_method_after_sale == "fixed":
                total_after_discount = (
                    rec.total_without_discount
                    - rec.total_discount
                    - rec.discount_after_sale
                )
            if rec.discount_method_after_sale == "percentage":
                total_after_discount = (
                    rec.total_without_discount
                    - rec.total_discount
                    - (
                        (rec.total_without_discount - rec.total_discount)
                        * rec.discount_after_sale
                        / 100.0
                    )
                )
            rec.total_after_discount = total_after_discount

    @api.depends(
        "discount_after_sale",
        "total_discount_after_sale_by_product",
    )
    def _compute_total_discount_after_sale_percentage(self):
        for rec in self:
            rec.total_discount_after_sale_percentage = (
                rec.discount_after_sale * rec.total_discount_after_sale_by_product
            ) / 100

    @api.depends(
        "total_without_discount",
        "total_discount",
        "discount_method_after_sale",
        "discount_after_sale",
    )
    def _compute_total_discount_all(self):
        for rec in self:
            total_discount_all = 0
            if rec.discount_method_after_sale == "fixed":
                total_discount_all = rec.total_discount + rec.discount_after_sale

            if rec.discount_method_after_sale == "percentage":
                total_discount_all = rec.total_discount + (
                    (rec.total_without_discount - rec.total_discount)
                    * rec.discount_after_sale
                    / 100.0
                )
            rec.total_discount_all = total_discount_all

    @api.onchange("discount_method_after_sale")
    def _onchange_discount_method_after_sale(self):
        self.discount_after_sale = 0

    @api.onchange("discount_after_sale")
    def _onchange_discount_after_sale(self):
        if self.discount_after_sale > 100 or self.discount_after_sale < 0:
            self.discount_after_sale = 0
            raise ValidationError(_("Discount after sale should be valid"))

    @api.depends(
        "total_without_discount",
        "total_discount",
    )
    def _compute_total_discount_after_sale_by_product(self):
        for rec in self:
            rec.total_discount_after_sale_by_product = (
                rec.total_without_discount - rec.total_discount
            )

    @api.onchange("partner_id")
    def _onchange_obs_z_partner_id(self):
        if self.partner_id and not self.env.context.get("linked_from_appointment"):
            self.z_appointment_id = self.env["z_appointment.appointment"].search(
                [("customer_id", "=", self.partner_id.id)], limit=1, order="id desc"
            )

    @api.depends("invoice_line_ids")
    def _compute_invoice_type(self):
        for rec in self:
            line_count = len(rec.invoice_line_ids)
            product_lines = rec.invoice_line_ids.filtered(
                lambda l: l.product_id.detailed_type == "product"
            )
            service_lines = rec.invoice_line_ids.filtered(
                lambda l: l.product_id.detailed_type == "service"
            )

            if line_count == len(product_lines):
                rec.invoice_type = "product"
            elif line_count == len(service_lines):
                rec.invoice_type = "service"
            else:
                rec.invoice_type = "all"

    def button_export_invoice(self):
        action = self.env["ir.actions.report"]._for_xml_id(
            "z_obstetric.action_report_account_invoice"
        )
        return action
