/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { CharField, charField } from "@web/views/fields/char/char_field";
import { useRef } from "@odoo/owl";
import { useInputField } from "@web/views/fields/input_field_hook";


export class DecimalFieldBs extends CharField {
  setup() {
    this.input = useRef("input");
    const showDefault = this.props.showDefault; 

    useInputField({
      getValue: () => this.props.record.data[this.props.name] || "",
    });

  }

  static props = {
    id: { type: String, optional: true },
    name: { type: String },
    readonly: { type: Boolean, optional: true },
    record: { type: Object },
    autocomplete: { type: String, optional: true },
    isPassword: { type: Boolean, optional: true },
    placeholder: { type: String, optional: true },
    dynamicPlaceholder: { type: Boolean, optional: true },
    dynamicPlaceholderModelReferenceField: { type: String, optional: true },
    showDefault: {optional: true },
  };

  formatInput(value) {
    const formattedValue = value.replace(/[^0-9+\-\.]/g, "");
    const plusMinusMatch = formattedValue.match(/^[+\-]/);
    const rest = formattedValue.replace(/[+\-]/g, "");
    let newValue = plusMinusMatch ? plusMinusMatch[0] + rest : rest;
    const parts = newValue.split(".");
    if (parts.length > 2) {
      newValue = parts[0] + "." + parts.slice(1).join("");
    }
    return newValue;
  }

  async onBlur(e) {
    const formattedValue = this.formatInput(e.target.value);
    e.target.value = formattedValue;
    const saved = await this.props.record.update({ [this.props.name]: formattedValue });
  }

}
DecimalFieldBs.template = "z_web.DecimalFieldBs";

export const decimalFieldBs = {
  ...charField,
  component: DecimalFieldBs,
  extractProps: ({ attrs, options }) => ({
    dynamicPlaceholder: options.dynamic_placeholder || false,
    dynamicPlaceholderModelReferenceField:
        options.dynamic_placeholder_model_reference_field || "",
    autocomplete: attrs.autocomplete,
    placeholder: attrs.placeholder,
    showDefault: attrs.show_default || true,
}),
};

registry.category("fields").add("decimal_field_bs", decimalFieldBs);

