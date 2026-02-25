from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ZIcd10(models.Model):
    _name = "z_medical_record.icd_10"

    no = fields.Char("No")
    uid = fields.Char("Uid")
    title = fields.Char("Title")

    def unlink(self):
        raise UserError(
            _("ICD codes cannot be deleted as they are used for diagnosis.")
        )

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        if name:
            args += [
                "|",
                "|",
                ("no", operator, name),
                ("uid", operator, name),
                ("title", operator, name),
            ]
        fields = self.search(args, limit=limit)
        return fields.name_get()
