from odoo import api, fields, models, tools, _


class ZPartner(models.Model):
    _inherit = "res.partner"

    recipient_name = fields.Char(
        string="Recipient Name", size=25, compute="_compute_delivery_information"
    )
    recipient_phone = fields.Char(
        string="Recipient Phone", size=10, compute="_compute_delivery_information"
    )
    recipient_address = fields.Text(
        string="Recipient Address", compute="_compute_delivery_information"
    )
    glass_order_ids = fields.One2many(
        string="Glass Order",
        comodel_name="z_glass_order",
        inverse_name="customer_id",
    )

    def _compute_delivery_information(self):
        for rec in self:
            latest_order = self.env["z_glass_order"].search(
                [("customer_id", "=", rec.id), ("delivery_method", "=", "delivery")],
                order="create_date desc",
                limit=1,
            )
            if latest_order:
                rec.recipient_name = latest_order.recipient_name
                rec.recipient_phone = latest_order.recipient_phone
                rec.recipient_address = latest_order.recipient_address
            else:
                rec.recipient_name = False
                rec.recipient_phone = False
                rec.recipient_address = False
