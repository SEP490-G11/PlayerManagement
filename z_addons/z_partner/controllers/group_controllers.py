# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.z_web.helpers.response import ResponseUtils


class ZGroupController(http.Controller):
    @http.route("/z_partner/group", auth="user", methods=["GET"])
    def get_list_group(self):
        groups = (
            http.request.env["z_partner.group"].search([]).read(["id", "name", "code"])
        )
        return ResponseUtils.res(groups)
