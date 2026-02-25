# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.z_web.helpers.utils import ZUtils


class ZMedicalResult(models.Model):
    _inherit = "z_medical_record.medical_result"
    _rec_name = "title"

    title = fields.Char(string="Title", related="visit_id.title")
    cls_ids = fields.Many2many("product.product", domain="[('is_cls', '=', True)]", string="Cls", tracking=True)
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
    )

    @api.model_create_multi
    def create(self, values):
        for value in values:
            prefix = (f"{value['code']}{ZUtils.format_datetime(ZUtils.str_to_date(value['examination_date']), '%y%m%d')}")
            count_env = self.env["z_ophthalmonogy.examination_count"]
            examination_count_record =  count_env.search([("prefix","=",prefix)],limit = 1)
            
            if examination_count_record:
                examination_count_record.count += 1
                value["code"] = (
                    f"{prefix}{examination_count_record.count:03d}"
                )
            else:
                value["code"] = (
                    f"{prefix}{1:03d}"
                )
                count_env.create({
                    "prefix": prefix,
                    "count": 1
                })
            return super().create(value)
