from odoo import models, fields, api, _


class ZOvalutionChecking(models.Model):
    _name = "z_obstetric.oval_check_idc"
    _inherit = ["z_medical_record.medical_result"]
    _description = "Ovalution checking indicated" 
    
    menstrual = fields.Text("Menstrual")  # Kinh nguyệt
    menstrual_cycle = fields.Text("Cycle")  # Chu kì
    kcc = fields.Text("KCC") #KCC 
    position = fields.Text("Position")  # Tư thế
    size = fields.Text("Size(mm)")  # Kích thước (mm)
    other_image = fields.Text("Other image")  # Hình ảnh khác
    mocous_douglas = fields.Text("Mocous Douglas")  # Dịch cùng đồ
    cheking_ids = fields.One2many("z_obstetric.ovalution_checking", "indicated_id",string="Chekings")
    is_save = fields.Boolean("Is save", default=False, tracking=True)

    @api.model
    def create(self, vals):
        vals["is_save"] = True
        record = super(ZOvalutionChecking, self).create(vals)
        return record