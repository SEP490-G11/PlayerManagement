from odoo import models, fields, _

class ZOvalutionChecking(models.Model):
    _name = "z_obstetric.ovalution_checking"
    
    date = fields.Date("Date") #Ngày
    period_day = fields.Text("Period Day")# Ngày chu kì
    mucosa = fields.Text("Mucosa")  # Niêm mạc
    left_ovary = fields.Text("Left ovary")  # Buồng trứng trái
    right_ovary = fields.Text("Right ovary")  # Buồng trứng phải
    mocous_douglas = fields.Text("Mocous Douglas")  # Dịch cùng đồ
    
    indicated_id = fields.Many2one("z_obstetric.oval_check_idc", string = "Indicated")