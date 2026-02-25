/** @odoo-module **/

export default {
  /**
   * @param {String} dateString
   * @summary Convert string YYYY/MM/DD to DD-MM/-YYYY
   * @returns {String} str formart DD-MM-YYYY
   */
  convertToDate(dateString) {
    if (dateString) {
      const d = dateString.split("/");
      return `${d[2]}-${d[1]}-${d[0]}`;
    } else {
      return "";
    }
  },

  /**
   * @param {String} str
   * @summary Convert number of string to format currency (1000 -> 1.000) and remove first character if it is 0
   * @returns {String} str formart DD-MM-YYYY
   */
  formatCurrency(input) {
    if (input === 0) {
      return input;
    }
    if (typeof input === "number") {
      input = input.toString();
    }
    if (isNaN(input[0]) || input[0] == "0") {
      return "";
    }
    if (typeof input === "string") {
      const cleanInput = input.replace(/\D/g, "");
      const match = cleanInput.match(/^(\d+)(?:\.(\d+))?$/);
      if (!match) {
        return input;
      }
      return cleanInput.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }
    return input;
  },

  /**
   * @param {String} str
   * @summary format currency to number (1.000 -> 1000)
   * @returns {Number} number
   */
  convertCurrencyToNumber(input) {
    const cleanInput = input.toString().replace(/\D/g, "");
    const newInt = parseInt(cleanInput, 10);
    if (isNaN(newInt)) {
      return input;
    }
    return newInt;
  },

  /**
   * @param {String} limit
   * @summary check if limit is empty then return "Không giới hạn"
   * @returns {String} limit
   */
  getLimitLabel(limit) {
    if (limit == "") {
      return "Không giới hạn";
    }
    return limit;
  },

  containsWhiteSpace(inputString) {
    let whitespacePattern = /\s/;
    return whitespacePattern.test(inputString);
  },

  containsSpecialChar(inputString) {
    let specialCharPattern = /[!@#$%^&*(),.?":{}|<>]/;
    return specialCharPattern.test(inputString);
  },

  containsSpecialCharOrSpace(inputString) {
    if (inputString.includes("_")) return true;
    if (inputString.includes(" ")) return true;
    const specialCharPattern = /[^\w\s]+/;
    return specialCharPattern.test(inputString);
  },

  containsVietnameseChar(inputString) {
    const vietnameseCharPattern = /[\u00C0-\u1EF9\u1EFB-\u1EFD\u1E80-\u1EF1]/;
    return vietnameseCharPattern.test(inputString);
  },
};
