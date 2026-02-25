/** @odoo-module **/

import { registry } from "@web/core/registry";
import { RadioField, radioField } from "@web/views/fields/radio/radio_field";

export class EmployeeGenderRadio extends RadioField {

  setup() {
    super.setup();
    this.props.autosave = true;
  }

  get hierarchyItems() {
    const filterValue = ["other"];
    return this.items.filter((o) => !filterValue.includes(o[0]));
  }
}

EmployeeGenderRadio.template = "z_hr.EmployeeGenderRadio";

export const employeeGenderRadio = {
  ...radioField,
  component: EmployeeGenderRadio,
};

registry.category("fields").add("employee_gender_radio", employeeGenderRadio);
