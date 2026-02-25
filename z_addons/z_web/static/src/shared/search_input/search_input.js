/** @odoo-module **/

const { Component, useState, onWillUpdateProps } = owl;
import utils from "../../utils";

export class SearchInput extends Component {
  static props = {
    value: String,
    onChange: Function,
    class: String,
    isDisable: { type: Boolean, optional: true },
    placeholder: String,
    value: String,
  };

  static defaultProps = {
    isDisable: false,
  };

  setup() {
    this.state = useState({
      input: "",
    });

    onWillUpdateProps((nextProps) => {
      if (nextProps.value == "") {
        this.state.input = "";
      }
    });
  }

  onSearch = utils.debounce((e) => {
    e.preventDefault();
    if (this.props.onChange) {
      this.props.onChange({ input: this.state.input });
    }
  });

  get classNames() {
    return this.props.isDisable ? `${this.props.class} disable` : this.props.class;
  }
  submit(e) {
    e.preventDefault();
  }
}

SearchInput.components = {};
SearchInput.template = "z_web.SearchInput";
SearchInput.defaultProps = {};
