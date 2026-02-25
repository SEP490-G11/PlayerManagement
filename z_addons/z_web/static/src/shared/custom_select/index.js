/** @odoo-module **/

const { Component, useState, onWillUpdateProps, onMounted } = owl;
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import utils from "../../utils";
export class CustomSelect extends Component {
  static props = {
    options: {
      type: Array,
      optional: false,
    },
    value: {
      type: Number,
      optional: true,
    },
    onChange: {
      type: Function,
      optional: true,
    },
    disabled: {
      type: Boolean,
      optional: true,
    },
    placeholder: {
      type: String,
      optional: true,
    },
    searchPlaceholder: {
      type: String,
      optional: true,
    },
  };

  static defaultProps = {
    disabled: false,
  };
  setup() {
    this.state = useState({
      selectedValue: null,
      label: "",
      searchText: "",
      _options: [],
      options: [],
    });
    onWillUpdateProps(async (nextProps) => {
      this.state.selectedValue = nextProps.value;
      this.state._options = nextProps.options;
    });
    onMounted(() => {
      this.dropdownRef = utils.getChildComponent(this, "Dropdown");
    });
  }

  get selectedLabel() {
    return this.props.options.find((option) => option.id === this.state.selectedValue)?.name || this.props.placeholder;
  }
  onChange(value) {
    if (value?.disabled) return;
    if (this.props.onChange) {
      this.props.onChange(value?.id || null);
    }
  }
  reset() {
    this.state.searchText = "";
    this.state.options = this.state._options;
  }
  onSearch() {
    this.state.options = this.state._options.filter((option) =>
      utils.searchNonVietnamese(option.name, this.state.searchText)
    );
  }
  submit(e) {
    e.preventDefault();
    if (this.state.searchText) {
      let o = this.state.options.at(0);
      this.onChange(o || null);
      this.dropdownRef.close();
    }
  }
}

CustomSelect.template = "z_web.CustomSelect";
CustomSelect.components = { Dropdown, DropdownItem };
