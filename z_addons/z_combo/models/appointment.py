from odoo import fields, models, api


class ZAppointment(models.Model):
    _inherit = "z_appointment.appointment"

    purchased_combo_line = fields.One2many(
        "z_combo.purchased.combo.line",
        "appointment_id",
        string="Purchased Combo Line",
        compute="_compute_purchased_combo_line",
        inverse="_inverse_purchased_combo_line",
    )

    @api.depends("customer_id", "customer_id.purchased_combo_line_ids")
    def _compute_purchased_combo_line(self):
        """Tự động cập nhật purchased_combo_line từ purchased_combo_line_ids của customer_id."""
        for appointment in self:
            if appointment.customer_id:
                appointment.purchased_combo_line = (
                    appointment.customer_id.purchased_combo_line_ids
                )
            else:
                appointment.purchased_combo_line = (
                    False  # Nếu không có customer_id, bỏ trống field
                )

    def _inverse_purchased_combo_line(self):
        """Khi purchased_combo_line thay đổi, cập nhật purchased_combo_line_ids trong res.partner."""
        for appointment in self:
            if appointment.customer_id:
                appointment.customer_id.purchased_combo_line_ids = [
                    (6, 0, appointment.purchased_combo_line.ids)
                ]

    def action_print_cls_for_today(self):
        pass
