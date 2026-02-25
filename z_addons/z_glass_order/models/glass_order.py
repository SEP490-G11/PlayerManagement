# -*- coding: utf-8 -*-
from unidecode import unidecode
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.addons.z_web.helpers.validation import ZValidation
from odoo.addons.z_web.helpers.utils import ZUtils


DELIVERY_METHOD_SELECTION = [
    ("clinic", "Clinic"),
    ("delivery", "Delivery"),
]

ORDER_DATE_METHOD_SELECTION = [
    ("now", "Now"),
    ("later", "Another Date"),
]

GLASS_ORDER_STATE = [
    ("received", "Received"),
    ("ordered", "Ordered"),
    ("pending", "Penidng"),
    ("cut", "Cut"),
    ("called", "Called Patient"),
    ("completed", "Completed"),
    ("incident", "Incident"),
    ("cared", "Cared"),
    ("care again", "Care Again"),
]


class ZGlassOrder(models.Model):
    _name = "z_glass_order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "zen8labs glass order"
    _rec_name = "title"

    title = fields.Char(string="Title", related="visit_id.title")
    code = fields.Char("Code", required=True, size=15)
    order_date = fields.Date(string="Order Date", default=fields.Date.today)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company.id
    )

    visit_id = fields.Many2one(
        comodel_name="z_appointment.appointment",
        string="Visit",
        domain="[('state','in', ('3', '4', '5', '6', '7', '8'))]",
        required=True,
    )
    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        related="visit_id.customer_id",
    )
    customer_group_id = fields.Many2one(
        related="customer_id.group_id", string="Customer Group", store=True
    )

    is_added = fields.Boolean("Is Added", default=False)
    is_paid = fields.Boolean("Is Paid", default=False)
    order_date_option = fields.Selection(
        selection=ORDER_DATE_METHOD_SELECTION,
        string="Order Date Option",
        store=False,
        default="now",
    )
    delivery_method = fields.Selection(
        selection=DELIVERY_METHOD_SELECTION,
        string="Delivery Method",
        required=True,
        default="clinic",
    )
    consultant = fields.Char("Consultant", required=True, size=25)
    cutter = fields.Char("Cutter", size=25)
    state = fields.Selection(
        selection=GLASS_ORDER_STATE,
        string="Status",
        copy=False,
        index=True,
        default="received",
        tracking=True,
    )
    note = fields.Text("Note", size=256, required=False)
    technician_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Technician",
        domain="[('bookable','=', True)]",
    )
    doctor_id = fields.Many2one(
        comodel_name="hr.employee", string="Doctor", domain="[('bookable','=', True)]"
    )
    right_eye = fields.Char(
        "Right Eye",
        size=25,
        compute="_compute_item_from_comprehensive",
        store=True,
        readonly=False,
    )
    left_eye = fields.Char(
        "Left Eye",
        size=25,
        compute="_compute_item_from_comprehensive",
        store=True,
        readonly=False,
    )
    add = fields.Char(
        "ADD",
        size=25,
        compute="_compute_item_from_comprehensive",
        store=True,
        readonly=False,
    )

    pupillary_distance = fields.Char("Pupillary Distance", required=False, size=10)
    pupillary_height = fields.Char("Pupillary Height", required=False, size=10)

    multifocal = fields.Boolean("Multifocal", default=True)
    bifocal = fields.Boolean("Bifocal", default=False)
    single_vision = fields.Boolean("Single Vision", default=False)
    far_vision = fields.Boolean("Far Vision", default=False)
    near_vision = fields.Boolean("Near Vision", default=False)

    examination_date = fields.Date(string="Examination Date")
    recipient_name = fields.Char(string="Recipient Name")
    recipient_phone = fields.Char(string="Recipient Phone")
    recipient_address = fields.Text(string="Recipient Address")
    # discount = fields.Integer(string="Discount", default=0)  # Commented out - removed discount feature
    amount = fields.Integer(string="Amount", compute="_compute_amount", store=True)
    customer_age = fields.Integer(
        string="Customer Age", related="visit_id.customer_age", store=True
    )
    glass_order_line_ids = fields.One2many(
        "z_glass_order.line", "glass_order_id", string="", copy=True
    )
    # sale_order_id = fields.Many2one(
    #     "sale.order",
    #     string="Related Sale Order",
    #     readonly=True,
    #     help="Sale order created from this glass order"
    # )
    # product_id = fields.Many2one(  # Commented out - removed related product
    #     "product.product",
    #     string="Related Product",
    #     domain=[("is_glass_order", "=", True)],
    # )
    glass_order_line_id_widget = fields.Json(
        string="Product List", compute="_compute_glass_order_widget"
    )
    products_glass_order_line = fields.Char(
        string="Product",
        compute="_compute_products_glass_order_line",
    )
    pdf_title = fields.Char(string="Pdf title", compute="_compute_pdf_title")

    # @api.constrains("discount")  # Commented out - removed discount feature
    # def _check_discount(self):
    #     for record in self:
    #         if record.discount < 0:
    #             raise ValidationError(_("Discount must be greater than 0."))

    @api.constrains("glass_order_line_ids")
    def _check_num_of_products(self):
        for record in self:
            for line in record.glass_order_line_ids:
                if line.quantity <= 0:
                    raise ValidationError(
                        _("The quantity of each product must be greater than 0.")
                    )

    # @api.depends("glass_order_line_ids", "discount")
    @api.depends("glass_order_line_ids")
    def _compute_amount(self):
        for rec in self:
            # total = sum(line.amount for line in rec.glass_order_line_ids) - rec.discount
            total = sum(line.amount for line in rec.glass_order_line_ids)
            rec.amount = total

    @api.depends("customer_id", "examination_date")
    def _compute_pdf_title(self):
        for record in self:
            name = unidecode(record.customer_id.name).replace(" ", "")
            title = _("GlassOrder")
            record.pdf_title = (
                f"{title}_{name}_{record.customer_id.code}_{record.examination_date}"
            )

    @api.depends("visit_id")
    def _compute_item_from_comprehensive(self):
        for rec in self:
            comprehensive = self.env["z_ophthalmology.comprehensive"].search(
                [("visit_id", "=", rec.visit_id.id)], limit=1
            )
            rec.right_eye = (
                comprehensive.right_eye_glasses_prescription if comprehensive else False
            )
            rec.left_eye = (
                comprehensive.left_eye_glasses_prescription if comprehensive else False
            )
            rec.add = comprehensive.add_glasses_prescription if comprehensive else False

    
    @api.model
    def create(self, vals):
        examination_count = self.env["z_appointment.examination_count"]
        prefix = f"DK{ZUtils.format_datetime(ZUtils.str_to_date(vals['examination_date']), '%y%m%d')}"
        examination_count_record = examination_count.search(
            [("prefix", "=", prefix)], limit=1
        )
        if examination_count_record:
            examination_count_record.count += 1
            vals["code"] = f"{prefix}{examination_count_record.count:04d}"
        else:
            examination_count.create({"prefix": prefix, "count": 1})
            vals["code"] = f"{prefix}{1:04d}"
        new_glass_order = super(ZGlassOrder, self).create(vals)
        # new_glass_order.create_and_write_sale_order()
        # Commented out - removed automatic product creation
        # category_id = (
        #     self.env["product.category"].search([("name", "=", "All")], limit=1).id
        # )
        # product_vals = {
        #     "name": (_("Glass Order") + f" {new_glass_order.code}"),
        #     "list_price": new_glass_order.amount,
        #     "glass_order_id": new_glass_order.id,
        #     "detailed_type": "product",
        #     "categ_id": category_id,
        #     "is_glass_order": True,
        # }
        # new_product = self.env["product.product"].create(product_vals)
        # new_glass_order.product_id = new_product.id
        return new_glass_order

    # @api.constrains(
    #     "delivery_method", "recipient_name", "recipient_phone", "recipient_address"
    # )
    # def constrains_recipient_name(self):
    #     for record in self:
    #         if record.delivery_method == "delivery":
    #             if (
    #                 not record.recipient_name
    #                 or not record.recipient_phone
    #                 or not record.recipient_address
    #             ):
    #                 raise ValidationError(_("Please fill delivery information."))
    #             ZValidation.validate_phone_number(record.recipient_phone)

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if len(self.search([("code", "=", rec.code)])) > 1:
                raise ValidationError(_("Glass order code is must be unique"))

    def write(self, vals):
        result = super(ZGlassOrder, self).write(vals)
        
        for glass_order in self:
            # product_vals = {}
            # if "code" in vals:
            #     product_vals["name"] = _("Glass Order") + f" {glass_order.code}"
            # product_vals["list_price"] = glass_order.amount
            # if product_vals:
            #     glass_order.product_id.write(product_vals)
            # if "glass_order_line_ids" in vals:
            #     glass_order.create_and_write_sale_order()
            if "recipient_name" in vals:
                glass_order.customer_id.write(
                    dict(recipient_name=vals.get("recipient_name"))
                )
            if "recipient_phone" in vals:
                glass_order.customer_id.write(
                    dict(recipient_phone=vals.get("recipient_phone"))
                )
            if "recipient_address" in vals:
                glass_order.customer_id.write(
                    dict(recipient_address=vals.get("recipient_address"))
                )
        return result

    def unlink(self):
        for record in self:
            if record.is_added:
                raise ValidationError(
                    _(
                        "The glasses order cannot be deleted because it has been added to the invoice."
                    )
                )
            # Commented out - removed product deletion logic
            # record = self.env["product.product"].search(
            #     [("glass_order_id", "=", record.id)]
            # )
            # record.unlink()
        return super(ZGlassOrder, self).unlink()

    @api.depends("glass_order_line_ids")
    def _compute_glass_order_widget(self):
        for rec in self:
            list_product = []
            for index, product in enumerate(rec.glass_order_line_ids):
                list_product.append(
                    {
                        "no": index + 1,
                        "name": product.product_id.name,
                        "quantity": product.quantity,
                        "code": (
                            product.product_id.default_code
                            if product.product_id.default_code
                            else ""
                        ),
                    }
                )
            rec.glass_order_line_id_widget = {"content": list_product}

    @api.depends("glass_order_line_ids")
    def _compute_products_glass_order_line(self):
        for rec in self:
            product_details = [
                f"{product.product_id.default_code + '/' if product.product_id.default_code else ''}{product.product_id.name}/{product.quantity}"
                for product in rec.glass_order_line_ids
            ]
            combined_details = ", ".join(product_details)
            rec.products_glass_order_line = combined_details

    @api.onchange("delivery_method")
    def _onchange_delivery_information(self):
        for rec in self:
            if (
                not rec.recipient_name
                and not rec.recipient_phone
                and not rec.recipient_address
            ):
                rec.recipient_name = (
                    rec.customer_id.recipient_name or rec.customer_id.name
                )
                rec.recipient_phone = (
                    rec.customer_id.recipient_phone or rec.customer_id.mobile
                )
                rec.recipient_address = (
                    rec.customer_id.recipient_address or rec.customer_id.street
                )

    @api.onchange("glass_order_line_ids")
    def _onchange_line_ids(self):
        products = self.glass_order_line_ids.mapped("product_id")
        for product in products:
            product_lines = self.glass_order_line_ids.filtered(
                lambda l: l.product_id == product
            )
            if len(product_lines) > 1:
                product_lines[0].quantity = sum(product_lines.mapped("quantity"))
                self.glass_order_line_ids = [(2, product_lines[1:].id, 0)]

    def action_print(self):
        action = self.env["ir.actions.report"]._for_xml_id(
            "z_glass_order.action_report_glass_order"
        )
        return action

    def action_print_pos(self):
        action = self.env["ir.actions.report"]._for_xml_id(
            "z_glass_order.action_report_pos_glass_order"
        )
        return action

    # def create_and_write_sale_order(self):
    #     """Create or update sale order from glass_order_line_ids"""
        
    #     # Skip if no products
    #     if not self.glass_order_line_ids:
    #         if self.sale_order_id:
    #             # If sale order exists but no products, delete all lines
    #             self.sale_order_id.order_line.unlink()
    #         return
            
    #     # Create sale order lines
    #     order_lines = []
    #     for line in self.glass_order_line_ids:
    #         order_line_vals = {
    #             'product_id': line.product_id.id,
    #             'name': f"{self.code}",  # Format: "DK240910001"
    #             'product_uom_qty': line.quantity,
    #             'price_unit': line.price,
    #             'product_uom': line.product_id.uom_id.id,
    #         }
    #         order_lines.append((0, 0, order_line_vals))

    #     if not self.sale_order_id:         
    #         # Create new sale order
    #         sale_order_vals = {
    #             'partner_id': self.customer_id.id,
    #             'date_order': fields.Datetime.now(),
    #             'order_line': order_lines,
    #             'glass_order_id': self.id,
    #         }
            
    #         sale_order = self.env['sale.order'].create(sale_order_vals)
    #         # Link the sale order back to glass order  
    #         self.sale_order_id = sale_order.id
    #     else: 
    #         sale_order = self.sale_order_id
    #         if not self.is_added:
    #             sale_order.write({
    #                 'order_line': [(5, 0, 0)] + order_lines  # Remove existing lines and add new ones
    #             })
        