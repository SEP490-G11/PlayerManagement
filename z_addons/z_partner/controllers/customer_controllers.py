# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import UserError

from odoo.addons.z_web.helpers.response import ResponseUtils
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_web.helpers.constants import ErrorCode


class ZCustomerController(http.Controller):
    @http.route("/z_partner/customer", auth="user", methods=["GET"])
    def get_list_customer(self, **kw):
        try:
            env = http.request.env["res.partner"]
            search_domain = [("is_customer", "=", True)]
            search_key = ZUtils.escape_special_characters(kw.get("input"))
            total_count = env.search_count(search_domain)
            pagination_info = ResponseUtils.get_paginated_info(total_count, kw)
            offset = pagination_info["offset"]
            if search_key:
                search_domain += [
                    "|",
                    "|",
                    "|",
                    ("name", "ilike", search_key),
                    ("code", "ilike", search_key),
                    ("mobile", "ilike", search_key),
                    ("z_mobile", "ilike", search_key),
                ]

            customers = (
                http.request.env["res.partner"]
                .search(
                    search_domain,
                    offset=offset,
                    limit=kw.get("page_size", 20),
                )
                .read(
                    [
                        "name",
                        "id",
                        "gender",
                        "group_id",
                        "contact_source",
                        "approach_channel",
                        "code",
                        "mobile",
                        "job",
                        "comment",
                        "date",
                        "street"
                    ]
                )
            )
            for customer in customers:
                customer["date"] = ZUtils.format_datetime(customer.get("date"))
            return ResponseUtils.res(dict(items=customers, **pagination_info))
        except UserError as code:
            return ResponseUtils.err(code=code)
        except Exception:
            return ResponseUtils.err(code=ErrorCode.INTERNAL_SERVER_ERROR)

    @http.route("/z_partner/customer/<int:id>", auth="user", methods=["GET"])
    def get_customer(self, id):
        try:
            customer = (
                http.request.env["res.partner"]
                ._get_customer_by_id(id)
                .read(
                    [
                        "name",
                        "id",
                        "gender",
                        "group_id",
                        "code",
                        "mobile",
                        "job",
                        "comment",
                        "date",
                        "street"
                    ]
                )[0]
            )
            customer["date"] = ZUtils.format_datetime(customer.get("date"))
            return ResponseUtils.res(customer)
        except UserError as code:
            return ResponseUtils.err(code=code)
        except Exception as e:
            return ResponseUtils.err(e)
