/** @odoo-module **/

const { Component, useState, onWillStart, onMounted } = owl;
import { registry } from "@web/core/registry";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { ScheduleForm } from "../schedule_form/schedule_form";
import { CustomDatePicker } from "@z_web/shared/datepicker/custom_datepicker";
import { SharedComponent } from "@z_web/shared";
import { ApiService } from "@z_web/services/api_service";
import { appointmentUrls, employeeUrls, placeUrls } from "../../config";
import { useService } from "@web/core/utils/hooks";

import {
  defaultPageData,
  defaultPageNumber,
  labelOptions,
  defaultAppointmentSort,
  appointmentSortOptions,
} from "@z_web/constants";
import { appointmentStateOptions, appointmentState, appointmentPrintingTypeOptions } from "@z_appointment/constants";
import utils from "@z_web/utils";
import { _t } from "@web/core/l10n/translation";

export class ScheduleTable extends Component {
  setup() {
    this.orm = useService("orm");
    this.action = useService("action");
    this.formRef = null;
    this.propsConfirm = {
      title: _t("Are you sure you want to delete the appointment?"),
      content: _t("Note: All appointment information will be deleted from the system."),
    };
    (this.stateList = appointmentStateOptions), (this.notArrivedState = appointmentState.NOT_YET_ARRIVED);
    this.printingTypes = appointmentPrintingTypeOptions;
    this.state = useState({
      isLoading: false,
      appointmentList: [],
      isEdit: false,
      activeId: false,
      pagingData: defaultPageData,
      start_date: "",
      end_date: "",
      queryParams: {
        start_date: "",
        end_date: "",
        input: "",
        doctor_ids: [],
        technician_ids: [],
        place_id: "",
      },
      place: null,
      places: [],
      stateList: appointmentStateOptions,
      sortOptions: appointmentSortOptions,
      defaultSort: defaultAppointmentSort,
      printingTypes: appointmentPrintingTypeOptions,
      doctorList: [],
      technicianList: [],
      isShowDoctorFilter: false,
      isShowTechnicianFilter: false,
      isShowGroupFilter: false,
    });
    onWillStart(() => {
      this.init();
    });
    onMounted(() => {
      this.formRef = utils.getChildComponent(this, "ScheduleForm");
    });
  }

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
        sort: this.state.defaultSort,
        start_date: utils.dateToYYYYMMDD(""),
        end_date: utils.dateToYYYYMMDD(""),
        place_id: this.state.place.id,
      };
      this.fetchAppointments(defaultPageNumber, queryParams);
    } catch (error) {
      console.error("An error occurred while fetching initial data:", error);
    }
  }

  async getListEmployee() {
    const res = await ApiService.call(
      employeeUrls.getListDoctorAndTechnician,
      { place_id: this.state.place.id },
      "get"
    );
    this.state.technicianList.length = 0;
    this.state.doctorList.length = 0;
    this.state.technicianList.push(...res.filter((item) => !item.is_doctor));
    this.state.doctorList.push(...res.filter((item) => item.is_doctor));
  }

  async getListPlace() {
    const res = await ApiService.call(placeUrls.crud, {}, "get");
    this.state.places = res;
  }

  //Update appointment state
  updateAppointmentState(id, state, is_visit) {
    ApiService.call(appointmentUrls.updateState + id, { id, state, is_visit }, "put")
      .then(() => {
        this.getAllAppointments(defaultPageNumber);
      })
      .catch((err) => {});
  }

  //Update appointment printing type
  updateAppointmentPrintingType(id, type) {
    ApiService.call(appointmentUrls.updatePrintingType + id, { id, type }, "put")
      .then(() => {
        this.getAllAppointments(defaultPageNumber);
      })
      .catch((err) => {});
  }

  getAllAppointments(pageNumber = defaultPageNumber) {
    this.fetchAppointments(pageNumber, this.state.queryParams);
  }

  // Call api get appoiment
  fetchAppointments(pageNumber = defaultPageNumber, params = {}) {
    this.state.queryParams = { ...this.state.queryParams, ...params, page_number: pageNumber };
    ApiService.call(appointmentUrls.crud, this.state.queryParams, "get").then((result) => {
      this.state.appointmentList = result.items.map((x) => ({
        ...x,
        format_booking_date: utils.YYYYMMDDToDDMMYYYY(x.booking_date),
      }));
      this.state.pagingData = utils.handleResponsePaging(result);
    });
  }

  // On filter schedule
  filterSchedule() {
    let doctorIds = [];
    let technicianIds = [];
    let states = [];

    utils.filterSelectedElement(this.state.doctorList, doctorIds);
    utils.filterSelectedElement(this.state.technicianList, technicianIds);
    utils.filterSelectedElement(this.state.stateList, states);

    this.fetchAppointments(defaultPageNumber, {
      doctor_ids: doctorIds,
      technician_ids: technicianIds,
      state: states,
    });

    return [doctorIds, technicianIds, states];
  }
  getLabelState(state) {
    return this.state.stateList.find((x) => x.value === state)?.label || "";
  }
  getLabelPrintingType(state) {
    return this.state.printingTypes.find((x) => x.value === state)?.label || "Vivision";
  }
  get nestedFilterOptions() {
    return [
      { id: 1, label: labelOptions.doctor, options: this.state.doctorList },
      { id: 2, label: labelOptions.technician, options: this.state.technicianList },
      { id: 3, label: labelOptions.state, options: this.state.stateList },
    ];
  }

  // On sort
  onSort(option) {
    this.fetchAppointments(defaultPageNumber, {
      sort: option,
    });
  }

  addAppointment() {
    this.openForm();
  }

  // On update schedule
  editAppointment(appointment) {
    this.openForm(appointment);
  }

  openForm(appointment = null) {
    this.formRef.openModal(appointment);
  }
  // On remove schedule
  onRemoveSchedule(schedule) {
    this.state.activeId = schedule.id;
  }

  removeSchedule() {
    this.state.isLoading = true;
    ApiService.call(appointmentUrls.crud + this.state.activeId, {}, "delete")
      .then(() => {
        this.fetchAppointments(defaultPageNumber, this.state.queryParams);
        $("#remove-confirm-modal").modal("toggle");
      })
      .finally(() => {
        this.state.isLoading = false;
      })
      .catch((error) => {
        const _error = {
          success: false,
          code: error.code || 500,
          message: "Không thể xóa được lịch khám vì đã có kết quả khám!",
          detail: error.detail,
          isShowToast: "isShowToast" in error ? error.isShowToast : true,
        };
        utils.showToast(_error);
      });
  }

  // Export data to excel
  async exportData() {
    utils.exportExcel(await ApiService.call(appointmentUrls.exportExcel, {}, "get"));
  }

  // On select time query
  selectTimeRange(event) {
    if (this.state.queryParams?.start_date && this.state.queryParams?.end_date) {
      this.fetchAppointments(defaultPageNumber, {
        ...this.state.queryParams,
      });
    } else if ((!this.state.queryParams.start_date && !this.state.queryParams.end_date) || !event.target.value) {
      this.fetchAppointments(defaultPageNumber, {});
    }
  }

  searchSchedules(searchText) {
    this.fetchAppointments(defaultPageNumber, { input: searchText });
  }

  onSearch(query) {
    utils.debounce(() => this.searchSchedules(query.input))();
  }

  // Show customer details modal
  showCustomerDetails(customer) {
    this.state.customerId = customer.id;
    this.state.customer = customer;
    $("#customerDetailFormModal").modal("toggle");
  }

  onUpdateStartDate(date) {
    this.state.queryParams.start_date = date;
    this.fetchAppointmentByTimeRange();
  }

  onUpdateEndDate(date) {
    this.state.queryParams.end_date = date;
    this.fetchAppointmentByTimeRange();
  }
  fetchAppointmentByTimeRange() {
    if (this.state.queryParams?.start_date && this.state.queryParams?.end_date) {
      this.fetchAppointments(defaultPageNumber, {
        ...this.state.queryParams,
      });
    } else {
      this.fetchAppointments(defaultPageNumber, {});
    }
  }
  async openAction(id) {
    const action = await this.orm.call("res.partner", "get_formview_action", [[id]], {
      context: { default_is_customer: 1, form_view_ref: "z_partner.view_partner_form" },
    });
    await this.action.doAction(action);
  }
  onClick(ev, id) {
    ev.preventDefault();
    ev.stopPropagation();
    this.openAction(id);
  }

  selectPlace(value) {
    this.state.place = value;
    this.getListEmployee();
    this.fetchAppointments(defaultPageNumber, {
      place_id: value.id,
    });
  }

  get isDisableBooking() {
    return !this.state.place;
  }
}

ScheduleTable.template = "z_appointment.ScheduleList";
ScheduleTable.components = SharedComponent.appendComponents({
  Dropdown,
  DropdownItem,
  ScheduleForm,
  // CustomerDetails,
  CustomDatePicker,
});

registry.category("actions").add("zen8.action_schedule_table", ScheduleTable);
