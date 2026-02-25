/** @odoo-module **/
import { registry } from "@web/core/registry";
import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { deleteConfirmationMessage } from "@web/core/confirmation_dialog/confirmation_dialog";
import utils from "@z_web/utils/toast";
export class TreeControllerWithToast extends ListController {
  setup() {
    super.setup();
    this.notification = useService("notification");
  }

  get deleteConfirmationDialogProps() {
    const root = this.model.root;
    const dataDelete = this.props?.dataDelete;
    let body = dataDelete?.body || deleteConfirmationMessage;
    if (root.isDomainSelected || root.selection.length > 1) {
      body = _t("Are you sure you want to delete these records?");
    }
    return {
      title: dataDelete?.title || _t("Bye-bye, record!"),
      body: body,
      confirm: async () => {
        try {
          await this.model.root.deleteRecords();
          utils.showToast(
            this.notification,
            utils.state.success,
            utils.type.success,
            utils.action.delete,
            this.props?.nameForm
          );
        } catch (e) {
          const message = utils.exceptions.includes(e?.data?.name) ? e?.data?.message : null;
          utils.showToast(
            this.notification,
            utils.state.error,
            utils.type.error,
            utils.action.delete,
            this.props?.nameForm,
            message
          );
        }
      },
      confirmLabel: _t("Delete"),
      cancel: () => {},
      cancelLabel: _t("No, keep it"),
    };
  }
}
TreeControllerWithToast.props = { ...ListController.props, nameForm: String, dataDelete: Object };
export const treeToastView = {
  ...listView,
  Controller: TreeControllerWithToast,
  props: (genericProps, view) => {
    const { ArchParser } = view;
    const { arch, relatedModels, resModel } = genericProps;
    const archInfo = new ArchParser().parse(arch, relatedModels, resModel);
    let nameForm = arch.getAttribute("string");
    nameForm = nameForm?.toLowerCase() || _t("object");
    let title = _t("Are you sure to delete the ${nameForm}?");
    let body = _t("Note: All ${nameForm} information will be deleted from the system.");
    title = title.replace("${nameForm}", nameForm);
    body = body.replace("${nameForm}", nameForm);
    return {
      ...genericProps,
      Model: view.Model,
      Renderer: view.Renderer,
      buttonTemplate: view.buttonTemplate,
      archInfo,
      nameForm,
      dataDelete: { title, body },
    };
  },
};
registry.category("views").add("tree_with_toast", treeToastView);
