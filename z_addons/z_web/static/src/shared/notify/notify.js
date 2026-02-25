/** @odoo-module **/

const { Component } = owl;

//---------------------------------------------------------------------
// Notify component
export class Notify extends Component {}
Notify.template = "z_web.Notify";

//---------------------------------------------------------------------
// NotifyError component
export class NotifyError extends Component {}
NotifyError.template = "z_web.NotifyError";

//---------------------------------------------------------------------
// NotifyWarning component
export class NotifyWarning extends Component {}
NotifyWarning.template = "z_web.NotifyWarning";

//---------------------------------------------------------------------
// Convert hash query to object
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

const timeInteval = setInterval(() => {
  // Init hightlight menu item when the first loading
  const currentParams = convertHashToObject(window.location.hash);
  const clinicManageMenu = document.querySelector("[data-menu-xmlid='z_web.menu_zen8_icare_clinic']");
  const inventoryManagementMenu = document.querySelector(
    "[data-menu-xmlid='z_web.menu_zen8_icare_inventory_management']"
  );
  const scheduleMenu = document.querySelector("[data-menu-xmlid='z_web.menu_zen8_icare_schedule']");
  const serivceMenu = document.querySelector("[data-menu-xmlid='z_web.menu_zen8_icare_service']");
  const billMenu = document.querySelector("[data-menu-xmlid='z_web.menu_zen8_icare_bill']");
  let action = parseInt(currentParams.action);

  if (action == 140 || action == 120 || action == 130 || (action > 94 && action < 98)) {
    if (clinicManageMenu) {
      $(clinicManageMenu).addClass("actived");
    }
  }

  if (action == 98 || action == 89) {
    if (scheduleMenu) {
      $(scheduleMenu).addClass("actived");
    }
  }

  if (action == 92 || action == 103 || action == 106) {
    if (inventoryManagementMenu) {
      $(inventoryManagementMenu).addClass("actived");
    }
  }

  if (action == 93 || action == 99) {
    if (serivceMenu) {
      $(serivceMenu).addClass("actived");
    }
  } else {
    document.querySelectorAll("[data-menu-xmlid]").forEach((el) => {
      if (el?.getAttribute("href")) {
        const elParams = convertHashToObject(el.getAttribute("href"));
        if (elParams.action == currentParams.action) {
          $(el).addClass("actived");
        } else {
          $(el).removeClass("actived");
        }
      }
    });
  }

  if (action == 110) {
    if (billMenu) {
      $(billMenu).addClass("actived");
    }
  } else {
    document.querySelectorAll("[data-menu-xmlid]").forEach((el) => {
      if (el?.getAttribute("href")) {
        const elParams = convertHashToObject(el.getAttribute("href"));
        if (elParams.action == currentParams.action) {
          $(el).addClass("actived");
        } else {
          $(el).removeClass("actived");
        }
      }
    });
  }

  // Add listener when user click to menu item, hightlight menu item
  document.querySelectorAll("a.o_nav_entry").forEach((el) => {
    el.addEventListener("click", () => {
      $(clinicManageMenu).removeClass("actived");
      $(scheduleMenu).removeClass("actived");
      $(inventoryManagementMenu).removeClass("actived");
      $(serivceMenu).removeClass("actived");
      $(billMenu).removeClass("actived");
      document.querySelectorAll("a.o_nav_entry").forEach((el) => {
        $(el).removeClass("actived");
      });
      $(el).addClass("actived");
    });
  });

  // Check if dropdown menu add event listener for handle click menu item
  if (clinicManageMenu) {
    clinicManageMenu.addEventListener("click", () => {
      document.querySelectorAll("a.o_nav_entry").forEach((el) => {
        $(el).removeClass("actived");
      });
      $(clinicManageMenu).addClass("actived");
      $(scheduleMenu).removeClass("actived");
      $(inventoryManagementMenu).removeClass("actived");
      $(serivceMenu).removeClass("actived");
      $(billMenu).removeClass("actived");
    });
  }

  // Check if dropdown inventory management menu add event listener for handle click menu item
  if (inventoryManagementMenu) {
    inventoryManagementMenu.addEventListener("click", () => {
      document.querySelectorAll("a.o_nav_entry").forEach((el) => {
        $(el).removeClass("actived");
      });
      $(inventoryManagementMenu).addClass("actived");
      $(scheduleMenu).removeClass("actived");
      $(clinicManageMenu).removeClass("actived");
      $(serivceMenu).removeClass("actived");
      $(billMenu).removeClass("actived");
    });
  }

  // Check if dropdown schedule menu add event listener for handle click menu item
  if (scheduleMenu) {
    scheduleMenu.addEventListener("click", () => {
      document.querySelectorAll("a.o_nav_entry").forEach((el) => {
        $(el).removeClass("actived");
      });
      $(scheduleMenu).addClass("actived");
      $(clinicManageMenu).removeClass("actived");
      $(inventoryManagementMenu).removeClass("actived");
      $(serivceMenu).removeClass("actived");
      $(billMenu).removeClass("actived");
    });
  }

  if (serivceMenu) {
    serivceMenu.addEventListener("click", () => {
      document.querySelectorAll("a.o_nav_entry").forEach((el) => {
        $(el).removeClass("actived");
      });
      $(serivceMenu).addClass("actived");
      $(scheduleMenu).removeClass("actived");
      $(clinicManageMenu).removeClass("actived");
      $(inventoryManagementMenu).removeClass("actived");
      $(billMenu).removeClass("actived");
    });
  }

  if (billMenu) {
    billMenu.addEventListener("click", () => {
      document.querySelectorAll("a.o_nav_entry").forEach((el) => {
        $(el).removeClass("actived");
      });
      $(billMenu).addClass("actived");
      $(serivceMenu).removeClass("actived");
      $(scheduleMenu).removeClass("actived");
      $(clinicManageMenu).removeClass("actived");
      $(inventoryManagementMenu).removeClass("actived");
    });
  }

  if (clinicManageMenu) {
    setTimeout(() => {
      clearInterval(timeInteval);
    }, 1000);
  }
}, 1000);
