/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { SelectionField, selectionField } from "@web/views/fields/selection/selection_field";
export class VisitStateSelection extends SelectionField {
  setup() {
    super.setup();
    this.props.autosave = true;
  }
  get hierarchyOptions() {
    return this.options;
  }
}
VisitStateSelection.template = "z_glass_order.VisitStateSelection";

export const visitStateSelection = {
  ...selectionField,
  component: VisitStateSelection,
};
registry.category("fields").add("z_medical_record_state_selection", visitStateSelection);
