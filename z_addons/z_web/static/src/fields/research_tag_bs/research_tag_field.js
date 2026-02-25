/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { Component, onWillUpdateProps, useState } from "@odoo/owl";

export class ResearchTagField extends Component {
  setup() {
    this.state = useState({
      color: this.props.record.data[this.props.name] ?? "white",
    });

    onWillUpdateProps((nextProps) => {
      console.log(nextProps);
      this.state.color = nextProps.record.data[nextProps.name] ?? "white";
    });
  }
}
ResearchTagField.template = "z_web.ResearchTag";

export const researchTagField = {
  component: ResearchTagField,
};

registry.category("fields").add("research_tag_field", researchTagField);
