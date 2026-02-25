/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { CharField, charField } from "@web/views/fields/char/char_field";
export class CustomerFieldBs extends CharField {
  setup() {
    super.setup();
  }
}
CustomerFieldBs.template = "z_web.CustomerFieldBs";

export const customerFieldBs = {
  ...charField,
  component: CustomerFieldBs,
};

registry.category("fields").add("customer_field_bs", customerFieldBs);
