/** @odoo-module **/

const { Component, useState } = owl;
import { labelOptions } from "@z_web/constants";
import utils from "../../utils";

export class TimeRange extends Component {
  static props = {
    fields: Object,
    onFetch: Function,
  };

  setup() {
    this.state = useState({
      fromLabel: labelOptions.from,
      toLabel: labelOptions.to,
      from: utils.dateToYYYYMMDD(new Date()),
      to: utils.dateToYYYYMMDD(new Date()),
    });
  }

  onChange(field, value) {
    if (this.props.onFetch) {
      let query = {};
      query[`${field}`] = value;
      this.props.onFetch(query);
    }
  }
}

TimeRange.components = {};
TimeRange.template = "z_web.TimeRange";
