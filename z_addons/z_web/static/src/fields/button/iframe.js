/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState } from "@odoo/owl";

export class IframeField extends Component {
  static props = {
    ...standardFieldProps,
  };

  setup() {
    super.setup(...arguments);
    this.url = this.props.record.data[this.props.name] ?? null;
    this.state = useState({
      isLoading: false
    })
  }

  onLoad(){
    this.state.isLoading = true
  }

}
IframeField.template = "z_web.CustomIframe";

export const iframeField = {
  component: IframeField,
};

registry.category("fields").add("button_upload_result", iframeField);
