/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { CharField, charField } from "@web/views/fields/char/char_field";
export class CharFieldBs extends CharField {
  setup() {
    super.setup();
  }
}
CharFieldBs.template = "z_web.CharFieldBs";

export const charFieldBs = {
  ...charField,
  component: CharFieldBs,
};

registry.category("fields").add("char_field_bs", charFieldBs);
