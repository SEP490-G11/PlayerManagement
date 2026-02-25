
from odoo import models

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        res = super().session_info()
        user = self.env.user
        res["user_context"]["user_place_ids"] = user.place_ids.ids
        return res