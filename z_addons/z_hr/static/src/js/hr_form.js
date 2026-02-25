/** @odoo-module **/
import { registry } from "@web/core/registry";
import { formToastView, FormControllerWithToast } from "@z_web/shared/form_with_toast";
import { _t } from "@web/core/l10n/translation";
import { useArchiveEmployee } from "@hr/views/archive_employee_hook";

export class HrFormController extends FormControllerWithToast {
  setup() {
    super.setup();
    this.archiveEmployee = useArchiveEmployee();
  }
  getStaticActionMenuItems() {
    const menuItems = super.getStaticActionMenuItems();
    menuItems.archive.callback = this.archiveEmployee.bind(this, this.model.root.resId);
    return menuItems;
  }
}
registry.category("views").add("hr_form", {
  ...formToastView,
  Controller: HrFormController,
});
