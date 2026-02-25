/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { SelectionField, selectionField } from "@web/views/fields/selection/selection_field";
import utils from "@z_web/utils/toast";
import { useService } from "@web/core/utils/hooks";

export class PrintingTypeSelection extends SelectionField {
  setup() {
    super.setup();
    this.props.autosave = true;
    this.notification = useService("notification");
  }
  get hierarchyOptions() {
    const filterValue = ["1"];
    return this.options.filter((o) => !filterValue.includes(o[0]));
  }
  async onChange(ev) {
    const value = JSON.parse(ev.target.value);
    try {
      const saved = await this.props.record.update({ [this.props.name]: value }, { save: true });
      if (saved) {
        utils.showToast(this.notification, utils.state.success, utils.type.success, utils.action.update, "");
      }
    } catch (e) {
      const message = utils.exceptions.includes(e?.data?.name) ? e?.data?.message : null;
      utils.showToast(this.notification, utils.state.error, utils.type.error, utils.action.update, "", message);
    }
  }
}
PrintingTypeSelection.template = "z_medical_record.PrintingTypeSelection";

export const printingTypeSelection = {
  ...selectionField,
  component: PrintingTypeSelection,
};

registry.category("fields").add("printing_type_selection", printingTypeSelection);
