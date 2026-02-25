/** @odoo-module **/

const { Component, useState, onWillStart, onWillUpdateProps } = owl;

export class Button extends Component {
  static props = {
    className: String,
    onClick: () => {},
    label: String,
    primary: Boolean,
    outline: Boolean,
    width: Number,
    height: Number,
    shortcutKey: "",
    isLoading: Boolean,
    disabled: Boolean,
  };

  setup() {
    this.state = useState({
      className: this.props.className,
    });
    onWillUpdateProps((nextProps) => {
      this.handleClassName(nextProps);
    });
    onWillStart(() => {
      this.handleClassName(this.props);
    });
  }

  // Change class name when button change state
  handleClassName(props) {
    if (props.isLoading || props.disabled) {
      this.state.className = this.state.className + " cursor-not-allowed";
    } else {
      this.state.className = this.state.className.replace("  cursor-not-allowed", "");
    }
  }
}
Button.template = "z_web.Button";
