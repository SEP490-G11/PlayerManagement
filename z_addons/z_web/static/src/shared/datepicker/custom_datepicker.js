/** @odoo-module **/
import utils from "../../utils";
import { DateTimeField } from "./datetime_field";
import { Component, onWillUpdateProps, useState } from "@odoo/owl";
const { DateTime } = luxon;

export class CustomDatePicker extends Component {
  setup() {
    this.state = useState({ parentProps: { ...this.props } });
    onWillUpdateProps(async (nextProps) => {
      this.state.parentProps = { ...nextProps };
    });
  }

  get datePickerProps() {
    const { parentProps } = this.state;
    let data = {};
    let model = {};
    if (parentProps.range) {
      data = {
        start: this.formatStringToDate(parentProps.value[0]),
        end: this.formatStringToDate(parentProps.value[1]),
      };
      model.endDateField = "end";
      model.startDateField = "start";
    } else {
      data[parentProps.name] = this.formatStringToDate(parentProps.value);
    }
    model = {
      alwaysRange: !!parentProps.range,
      name: parentProps.name,
      id: parentProps.id || "id",
      readonly: !!parentProps.readonly,
      record: {
        data,
        update: (e) => {
          if (parentProps.range) {
            parentProps.onChange([e.start.toISODate(), e.end.toISODate()]);
          } else if (e[parentProps.name]) {
            parentProps.onChange(e[parentProps.name].toISODate());
          } else {
            parentProps.onChange("");
          }
        },
        fields: { [parentProps.name]: { type: parentProps.type || "date" } },
        model: { bus: { trigger: () => {} } },
      },
      maxDate: this.formatDateToString(parentProps.maxDate),
      minDate: this.formatDateToString(parentProps.minDate),
      placeholder: parentProps.placeholder || "dd/mm/yyyy",
      required: parentProps.required,
      ...model,
      isInput: parentProps.isInput != undefined ? parentProps.isInput : true,
    };
    return model;
  }
  get formattedDisabledValue() {
    if (this.props.value) {
      return utils.dateToDDMMYYYY(new Date(this.props.value));
    }
    return "";
  }
  formatDateToString(date) {
    if (date instanceof Date) {
      return date.toISOString().slice(0, 10);
    }
    return date || "";
  }
  formatStringToDate(date) {
    if (date instanceof Date) {
      return DateTime.fromJSDate(date);
    } else if (date && typeof date === "string") {
      const newDate = new Date(date);
      return DateTime.fromJSDate(newDate);
    }
    return null;
  }
}

CustomDatePicker.template = "z_web.CustomDatePicker";
CustomDatePicker.components = {
  DatePicker: DateTimeField,
};
