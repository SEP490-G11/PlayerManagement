/** @odoo-module */
const { onMounted, onWillStart, useState } = owl;
import { patch } from "@web/core/utils/patch";
import { VisitStateSelection } from "../../../../../../z_medical_record/static/src/fields/visit_state_selection/visit_state_selection";
import { SharedComponent } from "@z_web/shared";
import { ConfirmStatusSchedule } from "../../views/schedule_table/confirm_status";
import { CustomModalController } from "../../views/popup_form/custom_popup_form";
import utils from "@z_web/utils/toast";

patch(VisitStateSelection.prototype, {
  setup() {
    super.setup();
    this.formRefConfirm = null;
    this.state = useState({
      props: null,
      notification: null,
      value: null,
      ev: null,
    });

    onWillStart(() => {
      this.state.value = this.props.record.data.state;
      if (!this.formRefConfirm) {
        this.formRefConfirm = new CustomModalController();
      }
    });

    onMounted(() => {
      this.formRefConfirm.props = {
        onSave: this.handleSave.bind(this),
      };
    });
  },

  async onChange(ev) {
    const value = JSON.parse(ev.target.value);
    const text = ev.target.selectedOptions[0].text;
    ev.target.value = `"${this.state.value}"`;
    this.state.ev = ev;
    if (text === "Đã kết luận" || text === "Finished") {
      this.state.props = this.props;
      this.state.notification = this.notification;
      this.formRefConfirm.openModal(value);
    } else {
      try {
        const saved = await this.props.record.update({ [this.props.name]: value }, { save: true });
        if (saved) {
          ev.target.value = `"${value}"`;
          this.state.value = value;
          utils.showToast(this.notification, utils.state.success, utils.type.success, utils.action.update, "");
        }
        if (value == "1") {
          var node = ev.target.parentElement.parentElement.parentElement;
          node.style.display = "none";
        }
      } catch (e) {
        const message = utils.exceptions.includes(e?.data?.name) ? e?.data?.message : null;
        utils.showToast(this.notification, utils.state.error, utils.type.error, utils.action.update, "", message);
      }
    }
  },

  async handleSave(event) {
    const { state } = event;
    try {
      const saved = await this.state.props.record.update({ [this.state.props.name]: state }, { save: true });
      if (saved) {
        this.state.ev.target.value = `"${state}"`;
        this.state.value = state;
        utils.showToast(this.state.notification, utils.state.success, utils.type.success, utils.action.update, "");
      }
      if (state == "1") {
        var node = ev.target.parentElement.parentElement.parentElement;
        node.style.display = "none";
      }
    } catch (e) {
      const message = utils.exceptions.includes(e?.data?.name) ? e?.data?.message : null;
      utils.showToast(this.state.notification, utils.state.error, utils.type.error, utils.action.update, "", message);
    }
  },
});

VisitStateSelection.components = SharedComponent.appendComponents({
  ConfirmStatusSchedule,
});
