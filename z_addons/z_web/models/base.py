# -*- coding: utf-8 -*-
from odoo import models, fields


class ZIrModelAccess(models.Model):
    _inherit = "ir.model.access"

    is_custom_access = fields.Boolean(string="Custom Access", default=False)


class Base(models.AbstractModel):
    _inherit = "base"

    def key_values(self, field, value):
        if isinstance(value[field], str):
            return f"{field} = '{value[field]}'"
        else:
            return f"{field} = {value[field]}"

    def write_force(self, vals):
        @self.env.cr.postrollback.add
        def write_force_postrollback():
            with self.pool.cursor() as cr_write:
                all_vals = ",".join([self.key_values(field, vals) for field in vals])
                cr_write.execute(
                    f"""UPDATE {self._table} SET {all_vals} where id = {self.id}"""
                )

        return self.write(vals)
