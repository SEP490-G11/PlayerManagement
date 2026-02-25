/** @odoo-module **/

import { nameConsts } from "@z_web/constants";
import utils from "@z_web/utils";
import validators from "@z_web/validators";

export default {
  ...validators,
  validatePerson(person, display = "") {
    const error = {};
    let isValid = true;
    error.name = validators.commonValidate(person.name, `tên ${display}`, { maxLength: 256 });
    error.mobile = validators.commonValidate(person.mobile, "số điện thoại");
    isValid = utils.checkEmptyKeys(error);
    return { isValid, error };
  },
};
