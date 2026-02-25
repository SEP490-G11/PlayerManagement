from odoo import api, fields, models
import json


class ZZNSHistory(models.Model):
    _name = "zns.history"
    _description = "Zns History History"

    customer_name = fields.Char(string="Name")
    data_id = fields.Integer(string="Data Id")
    phone = fields.Char(string="Phone")
    type = fields.Char(string="Type")
    status = fields.Char(string="Status")
    message = fields.Char(string="Message")
    data = fields.Json(string="Data")
    msg_id = fields.Char(string="MsgID", compute="_compute_msg_id", store=True)

    @api.depends("data")
    def _compute_msg_id(self):
        for record in self:
            msg_id = False
            if record.data:
                try:
                    # Kiểm tra nếu 'data' là dictionary hoặc chuỗi JSON
                    if isinstance(record.data, str):
                        # Giải mã chuỗi JSON ngoài cùng
                        data_dict = json.loads(record.data)
                    else:
                        data_dict = record.data

                    # Lấy chuỗi JSON bên trong 'original_data'
                    original_data_str = data_dict.get("original_data", "")
                    if original_data_str:
                        # Chuyển chuỗi JSON bên trong thành dictionary
                        original_data = json.loads(
                            original_data_str.replace("'", '"')
                        )  # Đổi nháy đơn thành nháy kép nếu cần
                        message = original_data.get("message")
                        nested_data = original_data.get("data", {})
                        if message == "Success":
                            msg_id = nested_data.get("msg_id")
                except json.JSONDecodeError:
                    # Xử lý lỗi nếu JSON không hợp lệ
                    msg_id = False
            record.msg_id = msg_id
