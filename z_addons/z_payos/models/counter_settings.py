from odoo import models, fields, api
from odoo.exceptions import UserError


class CounterSettings(models.Model):
    _name = 'z_payos.counter.settings'
    _description = 'System Settings'

    name = fields.Char(string='Counter Settings')
    banner_ids = fields.Many2many(string='Chụp ảnh', comodel_name='ir.attachment', context={'default_public': True,})

    @api.model
    def create(self, vals):
        if self.search_count([]) > 0:
            raise UserError("Only one record of system settings is allowed.")
        return super(CounterSettings, self).create(vals)

    @api.model
    def get_or_create(self):
        record = self.search([], limit=1)
        if not record:
            record = self.create({'name': 'default',})
        return record

    def get_init_data(self):
        cancel_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("z_payos.z_system_payos_cancel_url")
        )
        return_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("z_payos.z_system_payos_return_url")
        )
        user_id = self.env.user.id
        record = self.search([], limit=1)
        if not record or not record.banner_ids:
            return []
        return {
            "banner_ids": [
                {
                    "id": index + 1,
                    "title": attachment.name,
                    "url": f"/web/content/{attachment.id}",
                }
                for index, attachment in enumerate(record.banner_ids)
            ],
            "user_id": user_id,
            "return_url": return_url,
            "cancel_url": cancel_url,
        }
