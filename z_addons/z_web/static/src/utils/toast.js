/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";

export default {
  action: {
    add: _t("Add"),
    delete: _t("Delete"),
    update: _t("Update"),
  },
  type: {
    success: "success",
    error: "danger",
  },
  state: {
    success: _t("success"),
    error: _t("error"),
  },
  exceptions: ["odoo.exceptions.UserError", "odoo.exceptions.ValidationError"],
  showToast(notification, state, type, action, nameForm, msg = null) {
    msg = msg || `${action} ${nameForm} ${state}`;
    notification.add(msg, {
      type: type,
      sticky: false,
    });
  },
};
