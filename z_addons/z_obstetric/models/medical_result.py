from odoo import models, fields, _
from odoo.addons.z_web.helpers.utils import ZUtils


class ZMedicalResult(models.Model):
    _inherit = "z_medical_record.medical_result"
    _rec_name = "title"

    title = fields.Char(string="Title", related="visit_id.title")
    optometrist_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Optometrist",
        domain="[('bookable','=', True)]",
        tracking=True,
    )
    examiner_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Examiner",
        domain="[('bookable','=', True)]",
        tracking=True,
        required=True,
    )
    examination_date = fields.Date(
        "Examination date",
        tracking=True,
        required=True,
    )
    image_result_upload = fields.Many2many(string='Chụp ảnh', comodel_name='ir.attachment', context={'default_public': True,})

    def create(self, values):
        now = ZUtils.now()
        models = [
            "z_obstetric.gynecological",
            "z_obstetric.non_gynecological",
            "z_obstetric.post_pregnant",
            "z_obstetric.pre_pregnant",
            "z_obstetric.ultra_sound",
        ]
        domain = [
            ("create_date", ">=", f"{ZUtils.format_datetime(now, '%Y%m%d')} 00:00:00"),
            ("create_date", "<=", now),
        ]
        count = sum([self.env[mod].search_count(domain) for mod in models]) + 1
        return super().create(values)
    
    
