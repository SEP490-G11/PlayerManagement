/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { SelectionField, selectionField } from "@web/views/fields/selection/selection_field";
import utils from "@z_web/utils/toast";
import { useService } from "@web/core/utils/hooks";

export class VisitStateSelection extends SelectionField {
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
      if(value == "1"){
        var node = ev.target.parentElement.parentElement.parentElement;
        node.style.display ="none";
      }
      

    } catch (e) {
      const message = utils.exceptions.includes(e?.data?.name) ? e?.data?.message : null;
      utils.showToast(this.notification, utils.state.error, utils.type.error, utils.action.update, "", message);
    }
  }
}
VisitStateSelection.template = "z_medical_record.VisitStateSelection";

export const visitStateSelection = {
  ...selectionField,
  component: VisitStateSelection,
};

registry.category("fields").add("visit_state_selection", visitStateSelection);
