/** @odoo-module **/

export default {
  /**
   * @param {String} date
   * @param {String} time
   * @summary Convert string date and string time to datetime
   * @returns {Date}
   */
  DDMMYYYYToDate,
  YYYYMMDDToDate(str) {
    return new Date(str);
  },
  YYYYMMDDToDDMMYYYY(dateStr) {
    const date = new Date(dateStr);
    return this.formatDate(date);
  },
  formatDateYYYYMMDD(date) {
    const [day, month, year] = date.split("/");

    // Tạo đối tượng Date mới với định dạng "MM/DD/YYYY"
    const dateObject = new Date(`${month}/${day}/${year}`);

    // Lấy ngày, tháng, năm từ đối tượng Date mới
    const newDay = dateObject.getDate();
    const newMonth = dateObject.getMonth() + 1; // Tháng bắt đầu từ 0
    const newYear = dateObject.getFullYear();

    // Định dạng lại chuỗi kết quả
    return `${newYear}-${newMonth.toString().padStart(2, "0")}-${newDay.toString().padStart(2, "0")}`;
  },

  /**
   * @param {Date} date
   * @summary Convert date to string with format dd/mm/yyyy
   * @returns {String}
   */
  formatDate(date) {
    const day = date.getDate();
    const month = date.getMonth() + 1; // Tháng bắt đầu từ 0
    const year = date.getFullYear();
    return `${day < 10 ? "0" : ""}${day}/${month < 10 ? "0" : ""}${month}/${year}`;
  },

  /**
   * @param {Date} date
   * @summary Convert date to string with format yyyy-mm-dd
   * @returns {String}
   */
  dateToYYYYMMDD,

  /**
   * @param {Date} date
   *  @summary Convert date to string with format dd/mm/yyyy
   * @returns {String}
   */
  dateToDDMMYYYY(date) {
    if (date) {
      return `${date.getDate() < 10 ? "0" : ""}${date.getDate()}/${date.getMonth() + 1 < 10 ? "0" : ""}${
        date.getMonth() + 1
      }/${date.getFullYear()}`;
    }
  },

  setDateValue(dateValue) {
    return dateValue ? this.formatDateYYYYMMDD(dateValue) : null;
  },
};
function DDMMYYYYToDate(dtStr) {
  if (!dtStr) return null;
  let dateParts = dtStr.split("/");
  const _arr = dateParts[2].split(" ");
  let timeParts = _arr[1] ? _arr[1].split(":") : [];
  dateParts[2] = _arr[0];
  return new Date(
    Date.UTC(+dateParts[2], dateParts[1] - 1, +dateParts[0], timeParts[0] || 0, timeParts[1] || 0, timeParts[2] || 0)
  );
}
function dateToYYYYMMDD(date) {
  if (date) {
    return `${date.getFullYear()}-${date.getMonth() + 1 < 10 ? "0" : ""}${date.getMonth() + 1}-${
      date.getDate() < 10 ? "0" : ""
    }${date.getDate()}`;
  }
  return "";
}
