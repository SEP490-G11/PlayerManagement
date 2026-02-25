from odoo import api, fields, models
from odoo.addons.z_partner.helpers.constants import PartnerErrorCode
from odoo.addons.z_web.helpers.model_utils import ZModelUtils


class ZGroup(models.Model):
    _name = "z_partner.group"
    _description = "Group"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    code = fields.Char("Group code", tracking=True)
    name = fields.Char("Group name", tracking=True)

    def _get_group_by_id(self, group_id):
        return ZModelUtils.get_record_by_id(
            self, group_id, PartnerErrorCode.GROUP_DOES_NOT_EXIST
        )
