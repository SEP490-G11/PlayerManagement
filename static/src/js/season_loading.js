/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    async _onButtonClicked(ev) {
        if (ev.target?.name === "action_generate_schedule") {
            this.displayNotification({
                title: "Generating...",
                message: "Please wait while generating schedule.",
                type: "warning",
            });
        }
        return await super._onButtonClicked(ev);
    },
});