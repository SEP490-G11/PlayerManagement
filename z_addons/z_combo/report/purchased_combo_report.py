from odoo import models, fields


class PurchasedComboReport(models.Model):
    _name = "purchased.combo.report"
    _description = "Purchased Combo Report"
    _auto = False  # Dùng SQL View

    product_id = fields.Many2one("product.product", string="Tên SP/DV")
    account_move_id = fields.Many2one("account.move", string="Mã hoá đơn")
    account_move_code = fields.Char(string="Mã hoá đơn")
    invoice_date = fields.Date(string="Ngày hoá đơn")
    appointment_id = fields.Many2one("z_appointment.appointment", string="Mã lượt khám")
    appointment_code = fields.Char(string="Mã lượt khám")
    combo_parent_id = fields.Many2one("z_combo.combo", string="Gói combo cha")
    combo_parent_name = fields.Char(string="Gói combo cha")
    sub_combo_id = fields.Many2one("z_combo.combo", string="Gói combo thành phần")
    sub_combo_name = fields.Char(string="Gói combo cha")
    attach_combo_ids = fields.Many2many("z_combo.combo", string="Gói combo thành phần")
    product_price = fields.Float(string="Giá sản phẩm")
    combo_total = fields.Float(string="Thành tiền theo gói combo")
    combo_price_after_discount = fields.Float(string="Thành tiền theo gói combo")
    invoice_price_after_discount = fields.Float(string="Thành tiền ở hoá đơn")
    invoice_total = fields.Float(string="Thành tiền ở hoá đơn")
    quantity = fields.Integer(string="Số lượng")
    invoice_quantity = fields.Integer(string="Số lượng")
    payer_id = fields.Many2one("res.users", string="Người thanh toán")
    payer_name = fields.Char(string="Người thanh toán")
    executor_id = fields.Many2one("hr.employee", string="Người thực hiện")
    executor_name = fields.Char(string="Người thực hiện")

    def init(self):
        """Tạo hoặc cập nhật SQL View"""
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW purchased_combo_report AS
            SELECT
                pcl.id AS id,
                pcl.product_id AS product_id,
                pcl.account_move_id,
                am.invoice_date AS invoice_date,
                pcl.appointment_id,
                pcl.combo_id AS combo_parent_id,
                pt.list_price AS product_price,  -- Dùng list_price từ product_template
                (pcl.quantity * pt.list_price) AS combo_total,
                am.amount_total AS invoice_total,
                pcl.quantity AS quantity,
                am.create_uid AS payer_id,
                pcl.indicated_doctor AS executor_id,
                cl.price_after_discount AS combo_price_after_discount,
                CASE 
                    WHEN pt.detailed_type = 'service' AND aml.quantity > 0 THEN aml.price_total / aml.quantity
                    ELSE aml.price_total
                END AS invoice_price_after_discount,
                aml.quantity AS invoice_quantity,
                pcl.sub_combo_id AS sub_combo_id,
                am.code AS account_move_code,
                pcl.appointment_code AS appointment_code            
                
            FROM z_combo_purchased_combo_line pcl
            LEFT JOIN product_product pp ON pcl.product_id = pp.id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id  -- Join với product_template để lấy detailed_type
            LEFT JOIN account_move am ON pcl.account_move_id = am.id
            LEFT JOIN account_move_line aml ON aml.move_id = am.id AND aml.product_id = pcl.product_id  -- Join account_move_line để lấy giá sản phẩm
            LEFT JOIN z_combo_combo_line cl ON cl.combo_id = pcl.combo_id AND cl.product_id = pcl.product_id;  -- Join để lấy giá combo line

        """
        )
