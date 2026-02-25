/** @odoo-module */
const { onMounted, onWillStart } = owl;
import { patch } from "@web/core/utils/patch";
import { ScheduleTable } from "@z_appointment/views/schedule_table/schedule_table";
import { ApiService } from "@z_web/services/api_service";
import { appointmentUrls } from "@z_appointment/config/index";
import { appointmentState, appointmentStateOptions } from "../../constants/index";
import { defaultPageNumber, defaultAppointmentSortObstetric } from "@z_web/constants";
import { ConfirmStatusSchedule } from "./confirm_status";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { ScheduleForm } from "@z_appointment/views/schedule_form/schedule_form";
import { CustomDatePicker } from "@z_web/shared/datepicker/custom_datepicker";
import { SharedComponent } from "@z_web/shared";
import utils from "@z_web/utils";

patch(ScheduleTable.prototype, {
  setup() {
    super.setup();
    this.formRefConfirm = null;
    this.state.defaultSort = defaultAppointmentSortObstetric;
    (this.stateList = appointmentStateOptions), (this.notArrivedState = appointmentState.NOT_YET_ARRIVED);
    this.state.stateList = appointmentStateOptions

    onWillStart(() => {
      this.init();
    });
    onMounted(() => {
      this.formRef = utils.getChildComponent(this, "ScheduleForm");
      this.formRefConfirm = utils.getChildComponent(this, "ConfirmStatusSchedule");

      this.formRefConfirm.props = {
        onSave: this.handleSave.bind(this)
      };
    });
  },

  async init() {
    try {
      await this.getListPlace();
      this.state.place = this.state.places.length > 0 ? this.state.places[0] : null;
      if (!this.state.place) {
        return;
      }
      await this.getListEmployee();

      const queryParams = {
        ...this.state.queryParams,
        sort: defaultAppointmentSortObstetric,
        start_date: utils.dateToYYYYMMDD(new Date(Date.now())),
        end_date: utils.dateToYYYYMMDD(new Date(Date.now())),
        place_id: this.state.place.id,
      };
      this.fetchAppointments(defaultPageNumber, queryParams);
    } catch (error) {
      console.error("An error occurred while fetching initial data:", error);
    }
  },

  //Update appointment state
  updateAppointmentState(id, state, is_visit) {
    if (state === appointmentState.FINISHED) {
      this.formRefConfirm.openModal(true, { id, state, is_visit });
    } else {
      this.formRefConfirm.openModal(false, null);
      ApiService.call(appointmentUrls.updateState + id, { id, state, is_visit }, "put")
        .then(() => {
          this.getAllAppointments(defaultPageNumber);
        })
        .catch((err) => {});
    }
  },

  handleSave(event) {
    const { id, state, is_visit } = event;
    ApiService.call(appointmentUrls.updateState + id, { id, state, is_visit }, "put")
      .then(() => {
        this.getAllAppointments(defaultPageNumber);
      })
      .catch((err) => {});
  },

  getLabelState(state) {
    return this.state.stateList.find((x) => x.value === state)?.label || "";
  }
});

ScheduleTable.components = SharedComponent.appendComponents({
  Dropdown,
  DropdownItem,
  ScheduleForm,
  CustomDatePicker,
  ConfirmStatusSchedule,
});
