/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useDateTimePicker } from "@web/core/datetime/datetime_hook";
import {
  areDatesEqual,
  deserializeDate,
  deserializeDateTime,
  formatDate,
  formatDateTime,
  today,
} from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
import { ensureArray } from "@web/core/utils/arrays";
/**
 * @typedef {luxon.DateTime} DateTime
 *
 * @typedef {import("../standard_field_props").StandardFieldProps & {
 *  endDateField?: string;
 *  maxDate?: string;
 *  minDate?: string;
 *  placeholder?: string;
 *  required?: boolean;
 *  rounding?: number;
 *  startDateField?: string;
 * }} DateTimeFieldProps
 *
 * @typedef {import("@web/core/datetime/datetime_picker").DateTimePickerProps} DateTimePickerProps
 */

/** @extends {Component<DateTimeFieldProps>} */
export class DateTimeField extends Component {
  static props = {
    name: { type: String },
    readonly: { type: Boolean, optional: true },
    record: { type: Object },
    endDateField: { type: String, optional: true },
    maxDate: { type: String, optional: true },
    minDate: { type: String, optional: true },
    alwaysRange: { type: Boolean, optional: true },
    placeholder: { type: String, optional: true },
    required: { type: Boolean, optional: true },
    rounding: { type: Number, optional: true },
    startDateField: { type: String, optional: true },
    id: { type: String, optional: true },
    isInput: { type: Boolean, optional: true },
  };

  static template = "z_web.DateTimeField";

  //-------------------------------------------------------------------------
  // Getters
  //-------------------------------------------------------------------------

  get endDateField() {
    return this.relatedField ? this.props.endDateField || this.props.name : null;
  }

  get field() {
    return this.props.record.fields[this.props.name];
  }

  get relatedField() {
    return this.props.startDateField || this.props.endDateField;
  }

  get startDateField() {
    return this.props.startDateField || this.props.name;
  }

  get values() {
    return ensureArray(this.state.value);
  }

  //-------------------------------------------------------------------------
  // Lifecycle
  //-------------------------------------------------------------------------

  setup() {
    const getPickerProps = () => {
      const value = this.getRecordValue();
      /** @type {DateTimePickerProps} */
      const pickerProps = {
        value,
        type: this.field.type,
        range: this.isRange(value),
      };
      if (this.props.maxDate) {
        pickerProps.maxDate = this.parseLimitDate(this.props.maxDate);
      }
      if (this.props.minDate) {
        pickerProps.minDate = this.parseLimitDate(this.props.minDate);
      }
      if (!isNaN(this.props.rounding)) {
        pickerProps.rounding = this.props.rounding;
      }
      return pickerProps;
    };

    const dateTimePicker = useDateTimePicker({
      target: "root",
      get pickerProps() {
        return getPickerProps();
      },
      onChange: () => {
        this.state.range = this.isRange(this.state.value);
      },
      onApply: () => {
        const toUpdate = {};
        if (Array.isArray(this.state.value)) {
          // Value is already a range
          [toUpdate[this.startDateField], toUpdate[this.endDateField]] = this.state.value;
        } else {
          toUpdate[this.props.name] = this.state.value;
        }
        // when startDateField and endDateField are set, and one of them has changed, we keep
        // the unchanged one to make sure ORM protects both fields from being recomputed by the
        // server, ORM team will handle this properly on master, then we can remove unchanged values
        if (!this.startDateField || !this.endDateField) {
          // If startDateField or endDateField are not set, delete unchanged fields
          for (const fieldName in toUpdate) {
            if (areDatesEqual(toUpdate[fieldName], this.props.record.data[fieldName])) {
              delete toUpdate[fieldName];
            }
          }
        } else {
          // If both startDateField and endDateField are set, check if they haven't changed
          if (
            areDatesEqual(toUpdate[this.startDateField], this.props.record.data[this.startDateField]) &&
            areDatesEqual(toUpdate[this.endDateField], this.props.record.data[this.endDateField])
          ) {
            delete toUpdate[this.startDateField];
            delete toUpdate[this.endDateField];
          }
        }

        if (Object.keys(toUpdate).length) {
          this.props.record.update(toUpdate);
        }
      },
    });
    // Subscribes to changes made on the picker state
    this.state = useState(dateTimePicker.state);
    this.openPicker = dateTimePicker.open;
  }

  //-------------------------------------------------------------------------
  // Methods
  //-------------------------------------------------------------------------

  /**
   * @param {number} valueIndex
   */
  getFormattedValue(valueIndex) {
    const value = this.values[valueIndex];
    return value ? (this.field.type === "date" ? formatDate(value) : formatDateTime(value)) : "";
  }

  /**
   * @returns {DateTimePickerProps["value"]}
   */
  getRecordValue() {
    if (this.relatedField) {
      return [this.props.record.data[this.startDateField], this.props.record.data[this.endDateField]];
    } else {
      return this.props.record.data[this.props.name];
    }
  }

  /**
   * @param {number} index
   */
  isDateInTheFuture(index) {
    return this.values[index] > today();
  }

  /**
   * @param {string} fieldName
   */
  isEmpty(fieldName) {
    return fieldName === this.startDateField ? !this.values[0] : !this.values[1];
  }

  /**
   * @param {DateTimePickerProps["value"]} value
   * @returns {boolean}
   */
  isRange(value) {
    if (!this.relatedField) {
      return false;
    }
    return this.props.alwaysRange || this.props.required || ensureArray(value).filter(Boolean).length === 2;
  }

  /**
   * @param {string} value
   */
  parseLimitDate(value) {
    if (value === "today") {
      return value;
    }
    return this.field.type === "date" ? deserializeDate(value) : deserializeDateTime(value);
  }

  /**
   * @return {boolean}
   */
  shouldShowSeparator() {
    return (
      (this.props.alwaysRange &&
        (this.props.readonly ? !this.isEmpty(this.startDateField) || !this.isEmpty(this.endDateField) : true)) ||
      (this.state.range &&
        (this.props.required || (!this.isEmpty(this.startDateField) && !this.isEmpty(this.endDateField))))
    );
  }
}
