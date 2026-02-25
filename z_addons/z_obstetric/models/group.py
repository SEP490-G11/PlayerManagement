from odoo import api, fields, models
from odoo.addons.z_web.helpers.model_utils import ZModelUtils


class ZGroup(models.Model):
    _inherit = "z_partner.group"

    def _get_group_by_id(self, group_id):
        return ZModelUtils.get_record_by_id(
            self, group_id, False
        )
