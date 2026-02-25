# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.z_web.helpers.response import ResponseUtils


class ZPlaceController(http.Controller):
    @http.route("/z_place/places", auth="user", methods=["GET"])
    def list(self, **kw):
        try:
            env = http.request.env["z_place.place"]
            search_domain = []
            records = env.search(search_domain)
            if len(records) == 0:
                return ResponseUtils.err(msg="Vui lòng tạo cơ sở để đặt lịch")
            result = [{"id": place.id, "name": place.name} for place in records]
            return ResponseUtils.res(result)
        except Exception as e:
            return ResponseUtils.err(e)
