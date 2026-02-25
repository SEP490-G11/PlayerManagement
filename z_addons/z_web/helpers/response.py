import json
from odoo.http import request
from odoo.addons.z_web.helpers.constants import ErrorCode, ERROR_MESSAGE_DICT


class ResponseUtils:
    @staticmethod
    def res(data={}, msg=""):
        return json.dumps(
            dict(
                code=None,
                message=msg,
                data=data,
            )
        )

    @staticmethod
    def err(code=ErrorCode.BAD_REQUEST_ERROR, msg="", detail={}):
        if not msg:
            msg = ERROR_MESSAGE_DICT.get(str(code)) or str(code)
        error_response = {"code": str(code), "message": str(msg), "detail": detail}
        return request.make_response(
            json.dumps(error_response),
            headers=[("Content-Type", "application/json")],
            status=400,
        )

    @staticmethod
    def get_paginated_info(total_count, page_info):
        page_number = int(page_info.get("page_number", "1"))
        page_size = int(page_info.get("page_size", "20"))
        offset = (page_number - 1) * page_size
        total_pages = -(-total_count // page_size)
        pages = list(range(1, total_pages + 1))

        start_record = (page_number - 1) * page_size + 1
        end_record = min(page_number * page_size, total_count)
        return dict(
            offset=offset,
            total_pages=total_pages,
            pages=pages,
            start_record=start_record,
            end_record=end_record,
            page_size=page_size,
            current_page=page_number,
            total_records=total_count,
        )
