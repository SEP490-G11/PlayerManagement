/** @odoo-module **/
const { Component, useState, onWillUpdateProps } = owl;
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

export class Filter extends Component {
  static props = {
    options: Array,
    onSelect: Function,
  };

  setup() {
    this.state = useState({
      selectedValue: this.props.default,
    });
    onWillUpdateProps((nextProps) => {
      this.state.selectedValue = nextProps.value;
    });
  }

  onSelect(value) {
    if (this.props.onSelect) {
      this.state.selectedValue = value;
      this.props.onSelect(value);
    }
  }
  get classActive() {
    return this.state.selectedValue ? "active" : "";
  }
}

Filter.components = {
  Dropdown,
  DropdownItem,
};
Filter.template = "z_web.Filter";
