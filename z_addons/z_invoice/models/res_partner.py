from odoo import api, fields, models, tools, _


class ZPartner(models.Model):
    _inherit = "res.partner"

    account_move_ids = fields.One2many(
        string="Invoices",
        comodel_name="account.move",
        inverse_name="partner_id",
        domain=[("move_type", "=", "out_invoice")],
    )
    account_move_entry_ids = fields.One2many(
        string="Invoices Entry",
        comodel_name="account.move",
        inverse_name="partner_id",
        domain=[("move_type", "=", "entry")],
    )
    account_payment_ids = fields.One2many(
        string="Account Payment",
        comodel_name="account.payment",
        inverse_name="partner_id",
    )

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        if name:
            args += [
                "|",
                "|",
                ("name", operator, name),
                ("mobile", operator, name),
                ("z_mobile", operator, name),
            ]
        fields = self.search(args, limit=limit)
        return fields.name_get()

    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.mobile:
                name = f"{name} - {record.mobile}"
            result.append((record.id, name))
        return result
