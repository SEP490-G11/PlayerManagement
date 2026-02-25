/** @odoo-module **/

import utils from "@z_web/utils";
import { nameConsts, regexConsts } from "@z_web/constants";

export default {
  commonValidate(value, display = "", options = {}, required = true) {
    if (typeof value === "string") {
      value = value.trim();
    }
    const { length = null, minLength = null, maxLength = null, specialCharOrSpace = false } = options;

    if (required && !value) {
      return `Không được để trống ${display}`;
    }

    if (length && value.length !== length) {
      return `Chỉ được nhập ${length} ký tự`;
    }

    if (minLength && value.length < minLength) {
      return `Nhập tối thiểu ${minLength} ký tự`;
    }

    if (maxLength && value.length > maxLength) {
      return `Chỉ được nhập tối đa ${maxLength} ký tự`;
    }

    if (specialCharOrSpace && utils.containsSpecialCharOrSpace(value)) {
      return "Chỉ được chứa chữ cái và số";
    }
    return null;
  },
  validateSelectOption(value, display) {
    if (!value) {
      return `Chưa chọn ${display}`;
    }
    return null;
  },
  validatePhoneNumber(value, options = {}, required = true) {
    const commonValidate = this.commonValidate(value, nameConsts.phoneNumber, options, required);
    if (commonValidate) {
      return commonValidate;
    }
    if (value && !regexConsts.phone.test(value)) {
      return `Số điện thoại không đúng định dạng`;
    }
    return null;
  },
};
