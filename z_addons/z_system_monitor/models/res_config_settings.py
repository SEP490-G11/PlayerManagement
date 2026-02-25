from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    z_system_monitor_webhook = fields.Char(
        string="Monitor Webhook",
        config_parameter="z_system_monitor.z_system_monitor_webhook",
        default="https://z8ls.webhook.office.com/webhookb2/ff5f5a6e-6caa-45d4-aca6-aac3cbe68722@45f2ba3c-ef32-4fc3-b821-c5795bc014b0/IncomingWebhook/bb2c4b462e274fc78cc7a6edcd4a1950/998257e8-249a-42d6-9b67-bbcbf72774db",
    )
