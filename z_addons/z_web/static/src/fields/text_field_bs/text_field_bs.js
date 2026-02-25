/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { TextField, textField } from "@web/views/fields/text/text_field";
export class TextFieldBs extends TextField {
  setup() {
    super.setup();
  }
}
TextFieldBs.template = "z_web.TextFieldBs";

export const textFieldBs = {
  ...textField,
  component: TextFieldBs,
};

registry.category("fields").add("text_field_bs", textFieldBs);
