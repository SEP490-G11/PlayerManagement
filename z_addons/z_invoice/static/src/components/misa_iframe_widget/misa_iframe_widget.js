/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, onMounted } from "@odoo/owl";

export class MisaIframeWidget extends Component {
  static props = {
    ...standardFieldProps,
  };

  setup() {
    super.setup(...arguments);
    this.state = useState({
      isLoading: false
    });
    
    onMounted(() => {
      this.renderIframe();
    });
  }

  renderIframe() {
    const htmlContent = this.props.record.data[this.props.name];
    if (htmlContent && this.iframeContainer) {
      this.iframeContainer.innerHTML = htmlContent;
    }
  }

  onLoad() {
    this.state.isLoading = false;
  }
}

MisaIframeWidget.template = "z_invoice.MisaIframeWidget";

export const misaIframeWidget = {
  component: MisaIframeWidget,
};

registry.category("fields").add("misa_iframe", misaIframeWidget); 