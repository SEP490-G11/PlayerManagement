/** @odoo-module **/

const { Component, useState } = owl;

export class FormatInput extends Component {
  setup() {
    this.state = useState({
      value: this.props.value || "",
      error: "",
    });
  }

  onChangeInput(ev) {
    this.state.value = ev.target.value;
    this.props.value = this.state.value;
    if (this.props.format) {
      this.state.value = this.props.format(this.state.value);
    }
  }
}

FormatInput.template = "z_web.FormatInput";
FormatInput.props = {
  value: {
    type: String,
    optional: true,
  },
  error: {
    type: String,
    optional: true,
  },
  placeholder: {
    type: String,
    optional: true,
  },
  type: {
    type: String,
    optional: true,
  },
  disabled: {
    type: Boolean,
    optional: true,
  },
  autofocus: {
    type: Boolean,
    optional: true,
  },
  maxLength: {
    type: Number,
    optional: true,
  },
  format: Function,
};
