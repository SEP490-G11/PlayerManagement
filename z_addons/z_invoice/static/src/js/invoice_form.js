/** @odoo-module **/
import { registry } from "@web/core/registry";
import { formToastView, FormControllerWithToast } from "@z_web/shared/form_with_toast";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import {
  AccountMoveFormRenderer,
  AccountMoveFormCompiler,
} from "@account/components/account_move_form/account_move_form";
export class InvoiceFormController extends FormControllerWithToast {
  setup() {
    super.setup();
    this.account_move_service = useService("account_move");
  }
  async deleteRecord() {
    if (!(await this.account_move_service.addDeletionDialog(this, this.model.root.resId))) {
      return super.deleteRecord(...arguments);
    }
  }
}
registry.category("views").add("invoice_form", {
  ...formToastView,
  Controller: InvoiceFormController,
  Renderer: AccountMoveFormRenderer,
  Compiler: AccountMoveFormCompiler,
});
