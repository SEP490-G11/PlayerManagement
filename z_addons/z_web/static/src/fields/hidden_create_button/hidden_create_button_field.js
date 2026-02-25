/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";
import { ProductListField } from "@z_web/fields/product_list_field/product_list_field";

export class ButtonNearCreateButtonController extends ListController {
	setup() {
		super.setup();
	}

}
ButtonNearCreateButtonController.template = "z_web.HideCreatButton";
export const ButtonNearCreateButtonView = {
    ...listView,
    Controller: ButtonNearCreateButtonController,
};

registry.category("views").add("button_near_create_button", ButtonNearCreateButtonView);

