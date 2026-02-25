/** @odoo-module **/

const { Component, useState } = owl;
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

export class NestedFilter extends Component {
  static props = {
    nestedOptions: Array,
    onSelect: Function,
  };

  setup() {
    this.state = useState({
      toggleArray: [],
      nestedOptions: this.props.nestedOptions,
      isActive: false,
    });
  }

  setToggleFilter(id) {
    const toggleArray = [...this.state.toggleArray];
    const index = toggleArray.indexOf(id);
    const isArrayContainsId = index !== -1;

    if (!isArrayContainsId) {
      toggleArray.unshift(id);
    } else {
      toggleArray.splice(index, 1);
    }

    this.state.toggleArray = toggleArray;
  }

  isShowing(id) {
    return this.state.toggleArray.includes(id);
  }

  async select(nestedOptionId, option) {
    const value = this.getValuesOrIds(option);
    const optionFilter = this.getOption(nestedOptionId, value);
    optionFilter.selected = !optionFilter.selected;

    let checkedList = [];
    if (this.props.onSelect) {
      checkedList = await this.props.onSelect();
    }
    this.state.isActive = false;
    for (const arr of checkedList) {
      if (arr.length > 0) {
        this.state.isActive = true;
        break;
      }
    }
  }

  getChecked(nestedOptionId, option) {
    const value = this.getValuesOrIds(option);
    const optionFilter = this.getOption(nestedOptionId, value);
    return optionFilter.selected;
  }

  getOption(nestedOptionId, value) {
    const nestedOption = this.state.nestedOptions.find((nestedOption) => nestedOption.id === nestedOptionId);
    return nestedOption.options.find((option) => option.value === value || option.id === value);
  }

  getValuesOrIds(option) {
    return option.id ?? option.value;
  }

  getLabel(option) {
    return option.label ?? option.name;
  }
  get classActive() {
    return this.state.isActive ? "active" : "";
  }
}

NestedFilter.template = "z_web.NestedFilter";
NestedFilter.components = { Dropdown, DropdownItem };
