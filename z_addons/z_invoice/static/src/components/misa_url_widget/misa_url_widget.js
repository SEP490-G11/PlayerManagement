/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, onMounted } from "@odoo/owl";

export class MisaUrlWidget extends Component {
  static props = {
    ...standardFieldProps,
  };

  setup() {
    super.setup(...arguments);
    this.state = useState({
      isLoading: true
    });
    
    onMounted(() => {
      // Start with loading state when component mounts
      this.state.isLoading = true;
    });
  }

  get misaUrl() {
    return this.props.record.data['misa_url'] || '';
  }

  onLoad() {
    this.state.isLoading = false;
  }
  
  onError() {
    this.state.isLoading = false;
    // You could add error handling here if needed
  }
}

MisaUrlWidget.template = "z_invoice.MisaUrlWidget";

export const misaUrlWidget = {
  component: MisaUrlWidget,
};

registry.category("fields").add("misa_url_widget_1", misaUrlWidget); 