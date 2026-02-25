from odoo import api, fields, models
class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    z_system_payos_client_id = fields.Char(
        string="PayOS Client ID",
        config_parameter="z_payos.z_system_payos_client_id"
    )

    z_system_payos_api_key = fields.Char(
        string="PayOS API Key",
        config_parameter="z_payos.z_system_payos_api_key"
    )

    z_system_payos_checksum_key = fields.Char(
        string="PayOS Checksum Key",
        config_parameter="z_payos.z_system_payos_checksum_key"
    )
    
    z_system_payos_return_url = fields.Char(
        string="PayOS Return URL",
        config_parameter="z_payos.z_system_payos_return_url"
    )

    z_system_payos_cancel_url = fields.Char(
        string="PayOS Cancel URL",
        config_parameter="z_payos.z_system_payos_cancel_url"
    )
