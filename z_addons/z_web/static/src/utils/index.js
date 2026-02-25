/** @odoo-module **/

import string from "./string";
import array from "./array";
import object from "./object";
import datetime from "./datetime";
import number from "./number";
import calendar from "./calendar";

export default {
  ...string,
  ...array,
  ...object,
  ...datetime,
  ...number,
  ...calendar,
  isEmptyObj(obj) {
    if (!obj) return true;
    return Object.keys(obj).length === 0 && obj.constructor === Object;
  },
  searchNonVietnamese,
  showToast(res) {
    let toastEL;
    if (res) {
      if (res.success) {
        toastEL = $("#toastNotify");
      } else {
        toastEL = res.isWarning ? $("#toastNotifyWarning") : $("#toastNotifyError");
      }
      const toastBody = toastEL.find(".content");
      if (toastBody && res.message) {
        $(toastBody).html(`<span>${res.message}</span>`);
      }
      showMessage(toastEL);
    }
  },

  showToastUpdatingFunction() {
    this.showToast({
      isWarning: true,
      message: "Chức năng đang cập nhật",
    });
  },

  // Convert datepicker event to date string with format yyyy-mm-dd
  convertEventToDate(event) {
    return `${event.c.year}-${event.c.month < 10 ? "0" : ""}${event.c.month}-${event.c.day < 10 ? "0" : ""}${
      event.c.day
    }`;
  },

  generatePagingList(pages, currentPage, totalPages) {
    pages = pages.map((item) => {
      if ((item < currentPage + 3 && item > currentPage - 3) || item == 1 || item == totalPages) {
        return item;
      } else {
        return null;
      }
    });
    const newList = [];
    pages.forEach((item) => {
      if (newList.indexOf(item) == -1) {
        newList.push(item);
      }
    });
    if (pages && pages.length != 0) {
      return newList;
    } else {
      return [1];
    }
  },

  checkWorkingTimeIsValid(rangeTimeList) {
    let arr = rangeTimeList.filter((item) => {
      return item.fromTime === "" || item.toTime === "";
    });
    return arr.length === 0;
  },

  handleResponsePaging(result) {
    return {
      gotoPage: result.current_page,
      currentPage: result.current_page,
      totalRecords: result.total_records,
      totalPages: result.total_pages,
      pages: result.pages,
      startRecord: result.start_record,
      endRecord: result.end_record,
    };
  },

  debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        func.apply(this, args);
      }, timeout);
    };
  },

  warningDuplicate(isValidate, inputNames) {
    const inputs = document.querySelectorAll(inputNames.map((name) => `input[name="${name}"]`).join(","));
    inputs.forEach(function (input) {
      if (!isValidate) {
        input.classList.add("error-input");
      } else {
        input.classList.remove("error-input");
      }
    });
  },
  handleError(error, errorType) {
    const model = {};
    Object.keys(error).forEach(function (key) {
      if (error.code == errorType[key]) {
        model[key] = error.message;
        warningDuplicate(false, [key]);
      }
    });
    return model;
  },
  // Append default option to select
  appendDefaultOption(title, options) {
    return [{ id: null, name: title }, ...options];
  },

  validateEmail: (email) => {
    return String(email)
      .toLowerCase()
      .match(
        /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      );
  },
  exportExcel(result) {
    const link = document.createElement("a");
    link.href = result.url;
    link.download = result.filename;
    link.click();
  },

  hideForm(formName, resetFormHandler = null) {
    $(`#${formName}`).modal("hide");
    resetFormHandler && setTimeout(resetFormHandler, 100);
  },

  getChildComponent(obj, key) {
    let children = obj.__owl__.children;
    let ref = null;
    let keys = Object.keys(children);
    for (let i = 0; i < keys.length; i++) {
      if (children[keys[i]].name == key) {
        ref = children[keys[i]].component;
        break;
      }
    }
    return ref;
  },
};

function showMessage(toastEl) {
  toastEl.addClass("show");
  setTimeout(function () {
    toastEl.removeClass("show");
  }, 5 * 1000);
}

function convertHashToObject(hash) {
  hash = hash.replace("#", "");
  const parts = hash.split("&");
  const params = {};
  if (parts && parts.length != 0) {
    parts.forEach((item) => {
      const itemParts = item.split("=");
      params[itemParts[0]] = itemParts[1];
    });
  }
  return params;
}
function searchNonVietnamese(data, search) {
  let title = nonAccentVietnamese(data);
  let searchValue = nonAccentVietnamese(search);
  return title.includes(searchValue);
}
function nonAccentVietnamese(str) {
  str = str.toLowerCase();

  str = str.replace(
    /\u00E0|\u00E1|\u1EA1|\u1EA3|\u00E3|\u00E2|\u1EA7|\u1EA5|\u1EAD|\u1EA9|\u1EAB|\u0103|\u1EB1|\u1EAF|\u1EB7|\u1EB3|\u1EB5/g,

    "a"
  );

  str = str.replace(
    /\u00E8|\u00E9|\u1EB9|\u1EBB|\u1EBD|\u00EA|\u1EC1|\u1EBF|\u1EC7|\u1EC3|\u1EC5/g,

    "e"
  );

  str = str.replace(/\u00EC|\u00ED|\u1ECB|\u1EC9|\u0129/g, "i");

  str = str.replace(
    /\u00F2|\u00F3|\u1ECD|\u1ECF|\u00F5|\u00F4|\u1ED3|\u1ED1|\u1ED9|\u1ED5|\u1ED7|\u01A1|\u1EDD|\u1EDB|\u1EE3|\u1EDF|\u1EE1/g,

    "o"
  );

  str = str.replace(
    /\u00F9|\u00FA|\u1EE5|\u1EE7|\u0169|\u01B0|\u1EEB|\u1EE9|\u1EF1|\u1EED|\u1EEF/g,

    "u"
  );

  str = str.replace(/\u1EF3|\u00FD|\u1EF5|\u1EF7|\u1EF9/g, "y");

  str = str.replace(/\u0111/g, "d");

  // Some system encode vietnamese combining accent as individual utf-8 characters

  str = str.replace(/\u0300|\u0301|\u0303|\u0309|\u0323/g, ""); // Huyen sac hoi nga nang

  str = str.replace(/\u02C6|\u0306|\u031B/g, ""); // A, O, U

  return str;
}
