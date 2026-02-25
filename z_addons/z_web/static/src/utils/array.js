/** @odoo-module **/

export default {
  /**
   * @param {Array} arr1
   * @param {Array} arr2
   * @param modify arr2 by adding element with attribute is selected from arr1
   * @using for nested filter
   * @returns {Null}
   */
  filterSelectedElement(arr1, arr2) {
    arr1.forEach((element) => {
      if (element.selected) {
        arr2.push(element.id ?? element.value);
      }
    });
  },

  /**
   * @param {Array} arr
   * @returns {Array} arr with new reference
   * */
  cloneDeepArray(arr) {
    const cloneArr = [...arr];
    return cloneArr.map((item) => ({ ...item }));
  },
};
