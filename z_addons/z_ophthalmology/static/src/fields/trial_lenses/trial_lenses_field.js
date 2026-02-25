/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
const templateItem = { type: "", bc: "", p: "", dia: "", fitting: "", vision: "", over_rx: "", feeling: "" };
const templateData = [
  {
    label: "(1) Phải",
    position: 1,
    ...templateItem,
  },
  {
    label: "(1) Trái",
    position: 2,
    ...templateItem,
  },
  {
    label: "(2) Phải",
    position: 3,
    ...templateItem,
  },
  {
    label: "(2) Trái",
    position: 4,
    ...templateItem,
  },
  {
    label: "(3) Phải",
    position: 5,
    ...templateItem,
  },
  {
    label: "(3) Trái",
    position: 6,
    ...templateItem,
  },
];
export class TrialLenses extends Component {
  static template = "z_ophthalmology.TrialLenses";
  setup() {
    super.setup();
    let data = this.props.record.data[this.props.name] || [];
    data = templateData.map((x) => {
      return data.find((y) => y.position == x.position) || { ...x };
    });
    this.state = useState({
      data: data,
    });
  }
  onUpdate(event) {
    this.props.record.update({ [this.props.name]: this.state.data });
  }
  get isReadonly() {
    return !this.props.record.data.is_editable;
  }

}

export const trialLenses = {
  component: TrialLenses,
};

registry.category("fields").add("trial_lenses", trialLenses);
