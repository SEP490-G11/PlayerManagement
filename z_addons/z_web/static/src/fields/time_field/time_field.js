/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
const { Component } = owl;

export class TimeField extends Component {
  setup() {
    super.setup();
    this.format = this.props.format?? "HH:mm";
    this.time = this.props.record.data[this.props.name] ?? "";

  }


  formatDate(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    return `${hours}:${minutes}`;
  }
  
  adjustAndFormatDate() {
    const date = new Date(this.time);
    
    date.setHours(date.getHours() - 7);
    
    return this.formatDate(date);
  }
}
TimeField.template = "z_web.TimeField";

export const timeField = {
  component: TimeField,
};

registry.category("fields").add("time_field", timeField);
