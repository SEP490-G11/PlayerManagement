/** @odoo-module **/

const { Component, useState, onWillStart } = owl;
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { labelOptions } from "@z_web/constants";

export class Sort extends Component {
  setup() {
    this.state = useState({
      label: labelOptions.sort,
      sort: this.props.default,
      selectedValue: this.props.default,
    });
    onWillStart(async () => {});
  }

  onSelect(value) {
    if (this.props.onSelect && value) {
      this.state.selectedValue = value;
      this.props.onSelect(value);
    }
  }
  get classActive() {
    return this.state.selectedValue ? "active" : "";
  }
}

Sort.components = {
  Dropdown,
  DropdownItem,
};
Sort.template = "z_web.Sort";
