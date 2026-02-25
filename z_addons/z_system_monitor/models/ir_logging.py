from odoo import api, fields, models
import pymsteams
import logging

_logger = logging.getLogger(__name__)

DEFAULT_WEB_HOOK = "https://z8ls.webhook.office.com/webhookb2/ff5f5a6e-6caa-45d4-aca6-aac3cbe68722@45f2ba3c-ef32-4fc3-b821-c5795bc014b0/IncomingWebhook/bb2c4b462e274fc78cc7a6edcd4a1950/998257e8-249a-42d6-9b67-bbcbf72774db"


class ZIrLogging(models.Model):
    _inherit = "ir.logging"

    @api.model
    def create(self, vals):
        try:
            webhook_url = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("z_system_monitor.z_system_monitor_webhook")
            )
            record = super(ZIrLogging, self).create(vals)
            myTeamsMessage = pymsteams.connectorcard(webhook_url or DEFAULT_WEB_HOOK)

            teams_message = "<table>"
            for field in ["name", "path", "message", "func"]:
                if field in record:
                    field_label = self._fields[field].string
                    teams_message += "<tr><td style='min-width:100px;'>{}</td><td>{}</td></tr>".format(
                        field_label, record[field]
                    )
            teams_message += "</table>"

            myTeamsMessage.text("There is an error :" + teams_message)
            myTeamsMessage.send()
        except Exception as e:
            _logger.error("Failed to send message to Teams: %s", e)
        return record
