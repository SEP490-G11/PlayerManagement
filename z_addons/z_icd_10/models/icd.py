from odoo import models, fields, api


class ZIcd10(models.Model):
    _name = 'z_icd_10'
    _description = 'z_icd_10.z_icd_10'

    no = fields.Integer("No")
    uid = fields.Char("Uid")
    title = fields.Char("Title")

