/** @odoo-module **/
import { registry } from "@web/core/registry";
import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";

export class ListControllerNoSelectors extends ListController {
  setup() {
    super.setup();
  }
}

ListControllerNoSelectors.defaultProps = {
  allowSelectors: false,
  createRecord: () => {},
  editable: true,
  selectRecord: () => {},
  showButtons: true,
};

registry.category("views").add("no_selector_tree", {
  ...listView,
  Controller: ListControllerNoSelectors,
});
