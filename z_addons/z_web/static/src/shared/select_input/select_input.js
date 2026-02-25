/** @odoo-module **/

const { Component, useState } = owl;
import { nameConsts } from "@z_web/constants";
import utils from "../../utils";

export class SelectInput extends Component {
  static props = {
    options: {
      type: Array,
      optional: false,
    },
    selected: {
      type: Number,
      optional: true,
    },
    onChange: {
      type: Function,
      optional: true,
    },
    label: {
      type: String,
      optional: true,
    },
    isDisable: {
      type: Boolean,
      optional: true,
    },
  };

  static defaultProps = {
    disabled: false,
  };
  setup() {
    this.state = useState({});
  }

  get options() {
    return utils.appendDefaultOption(this.label, this.props.options);
  }

  get label() {
    return `Chọn ${this.props.label?.toLowerCase() || nameConsts.category}`;
  }

  onChange(event) {
    if (this.props.onChange) {
      this.props.onChange(event.target.value);
    }
  }

  onUpdatedQuantity(quantity, id, type) {
    if (this.props.onUpdatedQuantity) {
      this.props.onUpdatedQuantity(type, quantity, id);
    }
  }
}

SelectInput.template = "z_web.SelectInput";
