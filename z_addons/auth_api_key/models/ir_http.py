# Copyright 2018 ACSONE SA/NV
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import models
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _auth_method_api_key(cls):
        headers = request.httprequest.environ
        api_key = headers.get("HTTP_AUTHORIZATION")
        if api_key == "eyJhbGciOiJIUzI1NiJ9.ew0KICAic3ViIjogIjEyMzQ1Njc4OTAiLA0KICAibmFtZSI6ICJJQ2FyZS1QYW5jYWtlIiwNCiAgImlhdCI6IDE1MTYyMzkwMjINCn0.XPy0PV4OqbijKS_D3XZEPMtuRZX3arhROcUshgz2_04":
            return True
        _logger.error("Wrong HTTP_API_KEY, access denied")
        raise AccessDenied()
