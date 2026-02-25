# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class ZPurchasedComboLine(models.Model):
    _name = "z_combo.purchased.combo.line"

    combo_id = fields.Many2one("z_combo.combo", string="Combo")
    sub_combo_id = fields.Many2one("z_combo.combo", string="Sub Combo")
    partner_id = fields.Many2one("res.partner", string="Partner")
    indicated_doctor = fields.Many2one("hr.employee", string="Indicated Doctor")
    is_completed = fields.Boolean(string="Is Completed")
    is_indicated = fields.Boolean(string="Is Indicated")
    quantity = fields.Integer(string="Quantity")
    product_id = fields.Many2one("product.product", string="Combo details")
    appointment_id = fields.Many2one("z_appointment.appointment", string="Appointment")
    appointment_code = fields.Char(
        related="appointment_id.examination_code",
        string="Appointment Code",
        store=True,
        index=True,
    )
    indicated_date = fields.Date(
        string="Indicated Date", related="appointment_id.booking_date"
    )
    account_move_id = fields.Many2one("account.move", string="Invoice")

    @api.onchange("is_indicated")
    def _onchange_is_indicated(self):
        today = datetime.today().date()
        if self.is_indicated:
            appointment = self.env["z_appointment.appointment"].search(
                [
                    ("customer_id", "=", self.partner_id._origin.id),
                    ("booking_date", "=", today),
                    ("state", "!=", 1),
                ],
                limit=1,
                order="id desc",
            )
            if not appointment:
                raise UserError(
                    _("There is no appointment today for the indicated customer.")
                )
            else:
                self.appointment_id = appointment.id if appointment else False
        else:
            # Nếu bỏ check is_indicated, đặt appointment_id về False
            self.appointment_id = False

    def write(self, vals):
        # Kiểm tra nếu is_indicated đang được cập nhật
        if "is_indicated" in vals and not vals["is_indicated"]:
            for record in self:
                if record.is_indicated:  # Chỉ reset nếu trước đó là True
                    vals.update({"indicated_date": False, "appointment_id": False})
        return super(ZPurchasedComboLine, self).write(vals)
