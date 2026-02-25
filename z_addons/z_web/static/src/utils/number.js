/** @odoo-module **/

export default {
  isBetweenRange(valueStr, min, max) {
    const value = Number(valueStr.toString());
    return value ? (value >= min && value <= max) : false;
  },
}