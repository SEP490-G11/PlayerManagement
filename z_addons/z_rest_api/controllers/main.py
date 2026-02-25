from odoo.addons.base_rest.controllers import main


class ZRestApiController(main.RestController):
    _root_path = "/api/"
    _collection_name = "all.rest.api.services"
    _default_auth = "api_key"
