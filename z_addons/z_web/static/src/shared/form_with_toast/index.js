/** @odoo-module **/
import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { deleteConfirmationMessage } from "@web/core/confirmation_dialog/confirmation_dialog";
import utils from "@z_web/utils/toast";
export class FormControllerWithToast extends FormController {
  setup() {
    super.setup();
    this.notification = useService("notification");
  }
  async save(params) {
    const record = this.model.root;
    const id = record.evalContext?.id;
    let saved = false;
    let action = utils.action.add;
    if (id) action = utils.action.update;
    try {
      if (this.props.saveRecord) {
        saved = await this.props.saveRecord(record, params);
      } else {
        saved = await record.save(params);
      }
      if (saved && this.props.onSave) {
        this.props.onSave(record, params);
      }
      if (saved) {
        utils.showToast(this.notification, utils.state.success, utils.type.success, action, this.props?.nameForm);
      }
      return saved;
    } catch (e) {
      const message = utils.exceptions.includes(e?.data?.name) ? e?.data?.message : null;
      utils.showToast(this.notification, utils.state.error, utils.type.error, action, this.props?.nameForm, message);
    }
  }

  get deleteConfirmationDialogProps() {
    const dataDelete = this.props?.dataDelete;
    return {
      title: dataDelete?.title || _t("Bye-bye, record!"),
      body: dataDelete?.body || deleteConfirmationMessage,
      confirm: async () => {
        try {
          await this.model.root.delete();
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
        if (!this.model.root.resId) {
          this.env.config.historyBack();
        }
      },
      confirmLabel: _t("Delete"),
      cancel: () => {},
      cancelLabel: _t("No, keep it"),
    };
  }
}
FormControllerWithToast.props = { ...FormController.props, nameForm: String, dataDelete: Object };

export const formToastView = {
  ...formView,
  Controller: FormControllerWithToast,
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
      buttonTemplate: genericProps.buttonTemplate || view.buttonTemplate,
      Compiler: view.Compiler,
      archInfo,
      nameForm,
      dataDelete: { title, body },
    };
  },
};
registry.category("views").add("form_with_toast", formToastView);
