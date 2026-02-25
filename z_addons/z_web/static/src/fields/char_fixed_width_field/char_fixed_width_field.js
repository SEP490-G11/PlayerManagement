/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class TextFixedWidthField extends Component {
  setup() {
    this.value = this.props.record.data[this.props.name] ?? null;
  }
}
TextFixedWidthField.template = "z_web.TextFixedWidthField";

export const textFixedWidthField = {
  component: TextFixedWidthField,
};

registry.category("fields").add("tex_fixed_width_field_bs", textFixedWidthField);
