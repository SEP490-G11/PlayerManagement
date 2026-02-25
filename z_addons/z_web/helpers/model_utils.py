from odoo.exceptions import UserError


class ZModelUtils:
    @staticmethod
    def get_record_by_id(instance, record_id, error_code=None):
        record = instance.sudo().search([("id", "=", record_id)], limit=1)
        if not record and error_code:
            raise UserError(error_code)
        return record

    @staticmethod
    def check_unique_object(instance, record, fields, error_code, record_id=None):
        unique_conditions = [(field, "=", record[field]) for field in fields]
        exist = instance.search(unique_conditions, limit=1)
        if (exist and record_id is None) or (
            exist and record_id and exist.id != record_id
        ):
            raise UserError(error_code)
