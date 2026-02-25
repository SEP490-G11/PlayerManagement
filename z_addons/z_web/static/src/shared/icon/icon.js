/** @odoo-module **/

const { Component, useState } = owl;

export class Icon extends Component {
  static props = {
    size: String,
    name: String,
  };

  setup() {
    this.state = useState({
      name: this.props.name + ".svg",
      size: "icon-size-" + this.props.size,
    });
  }
}

Icon.components = {};
Icon.template = "z_web.Icon";
