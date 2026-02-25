from odoo.addons.web.controllers.export import ExportFormat
from odoo.addons.z_web.helpers.constants import EXPORT_DATE_FORMAT
from odoo.addons.z_web.helpers.utils import ZUtils

_super_filename = ExportFormat.filename


def filename(self, base):
    res = _super_filename(self, base)
    if base == "product.template":
        return f"Danh-sach-san-pham-{ZUtils.format_datetime(ZUtils.now(), EXPORT_DATE_FORMAT)}"
    return res


ExportFormat.filename = filename
