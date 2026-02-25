/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";
export class ProductListField extends Component {
  static props = {
    ...standardFieldProps,
  };

  setup() {
    this.list_product = this.props.record.data[this.props.name].content ?? []
  }
}
ProductListField.template = "z_web.ProductListField";

export const productListField = {
  component: ProductListField,
};

registry.category("fields").add("product_list_field", productListField);
