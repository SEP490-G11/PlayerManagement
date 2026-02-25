from odoo.addons.web.controllers.export import ExportFormat
from odoo.addons.z_web.helpers.constants import EXPORT_DATE_FORMAT
from odoo.addons.z_web.helpers.utils import ZUtils

_super_filename = ExportFormat.filename


def filename(self, base):
    res = _super_filename(self, base)
    format_datetime = ZUtils.format_datetime(ZUtils.now(), EXPORT_DATE_FORMAT)
    if base == "account.move":
        return f"Danh-sach-hoa-don-{format_datetime}"
    elif base == "account.payment":
        return f"Danh-sach-phieu-thu-{format_datetime}"
    return res


ExportFormat.filename = filename
