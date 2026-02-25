/** @odoo-module **/

export default {
  pick(object, ...properties) {
    return Object.fromEntries(properties.filter((prop) => prop in object).map((prop) => [prop, object[prop]]));
  },

  /**
   * @param {Object} obj
   * @returns {Object} obj with json type
   */
  parseToJson(obj) {
    return JSON.parse(JSON.stringify(obj));
  },
  /**
   * @param {Object} obj
   *  @returns {Object} obj with new reference
   */
  deepClone(obj) {
    if (obj === null || typeof obj !== "object") {
      return obj;
    }
    let clone = Array.isArray(obj) ? [] : {};
    for (let key in obj) {
      if (obj.hasOwnProperty(key)) {
        clone[key] = this.parseToJson(obj[key]);
      }
    }
    return clone;
  },
  /**
   * @param {Object} obj
   * @summary check object is empty
   *  @returns {Boolean} boolean
   */
  checkEmptyKeys(obj) {
    for (let key in obj) {
      if (obj.hasOwnProperty(key) && obj[key] !== null && obj[key] !== "") {
        return false;
      }
    }
    return true;
  },
};
