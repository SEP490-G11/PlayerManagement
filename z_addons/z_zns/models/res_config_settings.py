from odoo import api, fields, models
class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    z_system_zns_access_token = fields.Char(
        string="ZNS Access Token",
        config_parameter="z_zns.z_system_zns_access_token"
    )

    z_system_zns_refresh_token = fields.Char(
        string="ZNS Refresh Token",
        config_parameter="z_zns.z_system_zns_refresh_token"
    )

    z_system_zns_app_id = fields.Char(
        string="ZNS OA APP ID",
        config_parameter="z_zns.z_system_zns_app_id"
    )

    z_system_zns_secret_key = fields.Char(
        string="ZNS OA Secret Key",
        config_parameter="z_zns.z_system_zns_secret_key"
    )
