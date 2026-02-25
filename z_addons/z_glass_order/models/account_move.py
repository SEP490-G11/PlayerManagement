# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class ZAccountMove(models.Model):
    _inherit = "account.move"

    #Gôp lại ở phần link hoá đơn
    # @api.onchange("partner_id")
    # def _onchange_partner_id(self):
    #     new_products = self.env["account.move.line"]
    #     glass_orders = self.env["z_glass_order"].search(
    #         [("customer_id", "=", self.partner_id.id), ("is_added", "=", False)]
    #     )
    #     self.invoice_line_ids = new_products
    #     if glass_orders:
    #         for order in glass_orders:
    #             line_data = {
    #                 "product_id": order.product_id.id,
    #                 "quantity": 1,
    #                 "currency_id": self.currency_id,
    #                 "display_type": "product",
    #             }
    #             new_line = new_products.new(line_data)
    #             new_products += new_line
    #         self.invoice_line_ids += new_products

    def unlink(self):
        for record in self:
            glass_order = self._find_glass_order_by_line_name()
            if glass_order:
                glass_order.write({"is_added": False})
        return super(ZAccountMove, self).unlink()

    def write(self, vals):
        if "state" in vals:
            new_state = vals["state"]
            for record in self:
                glass_order = self._find_glass_order_by_line_name()
                if glass_order:
                    if new_state == "cancel":
                        glass_order.write({"is_added": False})
                        record.write({"invoice_line_ids": False})
                    else:
                        glass_order.write({"is_added": True})
        account_move_after = super(ZAccountMove, self).write(vals)
        return account_move_after

    def create(self, vals):
        new_account_move = super(ZAccountMove, self).create(vals)
        # for line in new_account_move.invoice_line_ids:
        #     if line.product_id.is_glass_order:
        #         if line.product_id.glass_order_id.is_added:
        #             raise ValidationError(_("Ops! This glass order is added in other invoice. Remove this from invoice to ceating"))
        #         line.product_id.glass_order_id.write({"is_added": True})
        return new_account_move

    def _find_glass_order_by_line_name(self):
        """Helper method to find glass order from line name that contains glass order code"""
        for record in self:
            for line in record.invoice_line_ids:
                if line.name and 'DK' in line.name:
                    glass_order = self.env['z_glass_order'].search([('code', '=', line.name)], limit=1)
                    if glass_order:
                        return glass_order

            return False

    @api.depends("amount_residual", "move_type", "state", "company_id")
    def _compute_payment_state(self):
        super(ZAccountMove, self)._compute_payment_state()
        for record in self:
            # Get the first line's name to find the glass order
            glass_order = self._find_glass_order_by_line_name()
            if glass_order:
                if record.payment_state == "paid":
                    glass_order.write({"is_paid": True})
                else:
                    glass_order.write({"is_paid": False})
