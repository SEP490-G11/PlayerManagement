/** @odoo-module **/

const { Component, useState, onMounted } = owl;
import { useService } from "@web/core/utils/hooks";

export class Breadcrumb extends Component {
  setup() {
    this.menuService = useService("menu");
    this.state = useState({ currentMenuName: "" });
    onMounted(async () => {
      new Promise((resolve, reject) => setTimeout(resolve, 50)).then(() => {
        const params = new URLSearchParams(window.location.hash.slice(1));
        this.state.currentActionId = params.get("action");
        this.updateBreadCrumb();
      });
    });
  }

  updateBreadCrumb() {
    const icareMenu = this.menuService.getCurrentApp();
    let breadcrumb = [];
    for (const menu of icareMenu.childrenTree) {
      breadcrumb = [];
      let isFound = false;
      if (menu.actionID && menu.actionID === parseInt(this.state.currentActionId)) {
        breadcrumb.push({ label: menu.name, active: true });
        break;
      } else {
        breadcrumb.push({ label: menu.name, active: false });
        if (menu.childrenTree.length > 0) {
          for (const child of menu.childrenTree) {
            if (child.actionID && child.actionID === parseInt(this.state.currentActionId)) {
              breadcrumb.push({ label: child.name, active: true });
              isFound = true;
              break;
            }
          }
        }
        if (isFound) {
          break;
        }
      }
    }
    // if (breadcrumb.length === 1) {
    //   breadcrumb.push({ ...breadcrumb[0] });
    //   breadcrumb[0].active = false;
    // }
    this.state.breadcrumb = breadcrumb;
  }
}

Breadcrumb.template = "z_web.Breadcrumb";
