/** @odoo-module **/

const { Component, useState, onWillStart, onMounted, useEffect } = owl;
import { CustomDatePicker } from "@z_web/shared/datepicker/custom_datepicker";
import { appointmentTypeOptions } from "@z_web/constants";
import { appointmentState } from "@z_appointment/constants";
import utils from "@z_web/utils";
import validators from "@z_appointment/validators";
import { loadJS } from "@web/core/assets";
import { ApiService } from "@z_web/services/api_service";
import { employeeUrls, timeSlotUrls, appointmentUrls, placeUrls } from "@z_appointment/config";
import { _t } from "@web/core/l10n/translation";
const { DateTime } = luxon;

import { CustomerForm } from "./customer_form";

export class ScheduleForm extends Component {
  setup() {
    this.customerFormRef = null;
    let maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 90);
    this.bookingType = {
      dateTime: 1,
      doctor: 2,
      technician: 3,
    };
    this.typeAppointments = [
      { value: this.bookingType.dateTime, label: _t("Date time"), icon: "/z_web/static/image/grey-calander.svg" },
      { value: this.bookingType.doctor, label: _t("Doctor"), icon: "/z_web/static/image/doctor.svg" },
      { value: this.bookingType.technician, label: _t("Technician"), icon: "/z_web/static/image/technician.svg" },
    ];
    const error = { type: "", booking_date: "", doctor_id: "", technician_id: "" };
    const appointment = {
      time_slot_id: 0,
      type: "1",
      overbook: false,
      examination_reason: "",
      state: appointmentState.NOT_YET_ARRIVED,
      note: "",
      technician_id: "",
      doctor_id: "",
      booking_type: 1,
      booking_date: "",
      booking_time: "",
      place_id: "",
    };
    this.state = useState({
      isEdit: false,
      isNotYetOccurred: true,
      isInitEdit: false,
      _appointment: null,
      maxDate: utils.dateToYYYYMMDD(maxDate),
      minDate: utils.dateToYYYYMMDD(new Date()),
      times: [],
      timeSlots: [],
      overbookTimeSlots: [],
      overbookTimes: [],
      filterTimeSlot: {},
      appointment: { ...appointment },
      defaultAppointment: { ...appointment },
      error,
      isLoading: false,
      isFetching: false,
      appointmentTypes: appointmentTypeOptions,
      doctors: [],
      technicians: [],
      technicianList: [],
      doctorList: [],
      places: [],
    });
    onWillStart(async () => {
      await loadJS("https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.30.1/moment.min.js");
    });
    onMounted(() => {
      this.customerFormRef = utils.getChildComponent(this, "CustomerForm");
    });
    useEffect(
      () => {
        this.state.canEdit =
          (!this.state.isEdit || (this.state.isNotYetArrived && this.state.isEdit)) && this.state.appointment.place_id;
      },
      () => [this.state.isNotYetArrived, this.state.isEdit, this.state.appointment.place_id]
    );

    useEffect(
      () => {
        this.state.isNotYetArrived = this.state.appointment.state == appointmentState.NOT_YET_ARRIVED;
      },
      () => [this.state.appointment.state]
    );

    useEffect(
      () => {
        const { booking_date, booking_time, doctor_id, technician_id, booking_type, overbook } = this.state.appointment;
        const id = booking_type == this.bookingType.technician ? technician_id : doctor_id;
        const arr = overbook ? this.state.overbookTimeSlots : this.state.timeSlots;
        this.state.appointment.time_slot_id =
          arr.find(
            (x) =>
              x.employee_id == id &&
              this.toDateTime(x.examination_date, x.start_time).isSame(moment(`${booking_date} ${booking_time}`))
          )?.id || "";
      },
      () => [
        this.state.appointment.booking_date,
        this.state.appointment.booking_time,
        this.state.appointment.doctor_id,
        this.state.appointment.technician_id,
        this.state.appointment.booking_type,
        this.state.appointment.overbook,
        this.state.overbookTimes,
        this.state.times,
      ]
    );
    useEffect(
      () => {
        const { overbook, booking_time, booking_date, booking_type, place_id } = this.state.appointment;
        if (!booking_time || !booking_date) return;
        const params = {
          overbook: overbook ? 1 : 0,
          expect_time: `${booking_date} ${booking_time}`,
          is_doctor: booking_type == this.bookingType.technician ? 0 : 1,
          place_id,
        };
        if (
          this.state._appointment &&
          this.state._appointment.booking_date === booking_date &&
          this.state._appointment.booking_time === booking_time
        ) {
          params.existIds = [this.state._appointment.doctor_id, this.state._appointment.technician_id];
          params.existIds = params.existIds.filter((x) => x);
        }
        this.handleGetEmployee(params).then((res) => {
          this.state.technicianList = res.filter((item) => !item.is_doctor);
          this.state.doctorList = res.filter((item) => item.is_doctor);
          if (this.state.appointment.booking_type == this.bookingType.technician && !this.state.doctorList.length) {
            this.state.error.doctor_id = "Không có bác sĩ làm việc trong giờ này";
          }
        });
      },
      () => [
        this.state.appointment.overbook,
        this.state.appointment.booking_time,
        this.state.appointment.booking_date,
        this.state.appointment.booking_type,
      ]
    );
    useEffect(
      () => {
        const { booking_date, booking_time } = this.state.appointment;
        if (booking_date && booking_time) {
          const timeString = `${booking_date} ${booking_time}`;
          this.state.isNotYetOccurred = moment(timeString).isAfter(moment());
        } else {
          this.state.isNotYetOccurred = true;
        }
      },
      () => [this.state.appointment.booking_date, this.state.appointment.booking_time]
    );
    useEffect(
      () => {
        if (this.state.isInitEdit) {
          this.state.isInitEdit = false;
        } else {
          this.resetSelectDoctorAndTechnician();
        }
      },
      () => [
        this.state.appointment.booking_date,
        this.state.appointment.overbook,
        this.state.appointment.booking_time,
        this.state.appointment.booking_type,
      ]
    );
    useEffect(
      () => {
        const params = {
          expect_date: this.state.appointment.booking_date,
          place_id: parseInt(this.state.appointment.place_id),
        };
        if (!params.expect_date) return;
        switch (parseInt(this.state.appointment.booking_type)) {
          case this.bookingType.dateTime:
            break;
          case this.bookingType.doctor:
            params.employee_id = parseInt(this.state.appointment.doctor_id);
            break;
          case this.bookingType.technician:
            params.employee_id = parseInt(this.state.appointment.technician_id);
            break;
        }
        if (JSON.stringify(params) !== JSON.stringify(this.state.filterTimeSlot)) {
          this.resetTimeSlot();
          this.state.filterTimeSlot = params;
          if ("employee_id" in params && !params.employee_id) return;
          this.getTimeSlot();
        }
      },
      () => [
        this.state.appointment.booking_date,
        this.state.appointment.doctor_id,
        this.state.appointment.technician_id,
        this.state.appointment.booking_type,
      ]
    );

    useEffect(
      () => {
        const placeId = parseInt(this.state.appointment.place_id);
        const params = isNaN(placeId) ? {} : { place_id: placeId };
        this.getListEmployee(params);

        if (!this.state.isEdit && !this.state._appointment && !this.state.appointment.booking_time) {
          this.state.appointment.doctor_id = "";
          this.state.appointment.technician_id = "";
          this.state.appointment.booking_date = "";
          this.resetTimeSlot();
        }
      },
      () => [this.state.appointment.place_id, this.state.isEdit]
    );
  }

  onSelectPlace(placeId) {
    const parsedPlaceId = parseInt(placeId);
    if (parsedPlaceId != parseInt(this.state.appointment.place_id)) {
      this.state.appointment.place_id = placeId;
      this.state.appointment.booking_date = "";
      this.resetTimeSlot(); 
    }
  }

  openModal(_appointment, date, time, place) {
    this.getListPlace();
    this.state.error = {};
    this.state.isEdit = !!_appointment;
    this.state.isInitEdit = false;
    this.state.appointment = {
      ...this.state.defaultAppointment,
      booking_date: date,
      booking_time: time,
      place_id: place,
    };
    if (_appointment) {
      this.state.isInitEdit = true;
      this.state.appointment = {
        ..._appointment,
        doctor_id: _appointment.doctor?.id || "",
        technician_id: _appointment.technician?.id || "",
      };
      this.state._appointment = { ...this.state.appointment };
    } else {
      this.state._appointment = null;
    }
    this.resetTimeSlot();
    this.customerFormRef.initForm(_appointment?.customer_id);
  }
  resetTimeSlot() {
    this.state.times = [];
    this.state.overbookTimes = [];
    this.state.timeSlots = [];
    this.state.overbookTimeSlots = [];
  }
  saveAppointment() {
    const validAppointmentForm = this.validAppointmentForm();
    const validCustomerForm = this.customerFormRef.validCustomerInfo();
    if (!validAppointmentForm || !validCustomerForm) return;
    const customer = this.customerFormRef.state.customer;
    const appointment = {
      ...this.state.appointment,
      customer: {
        id: customer.id,
        info: {
          group_id: customer.group_id,
          street: (typeof customer.street === 'string' ? customer.street : "").trim(),
          name: customer.name.trim(),
          date: customer.date.trim(),
          gender: (typeof customer.gender === 'string' ? customer.gender : "").trim(),
          mobile: customer.mobile.trim(),
          contact_source: customer.contact_source.trim(),
          approach_channel: customer.approach_channel,
          job: (typeof customer.job === 'string' ? customer.job : "").trim(),
          is_customer: true,
        },
      },
      booking_type: `${this.state.appointment.booking_type}`,
      time_slot_id: parseInt(this.state.appointment.time_slot_id),
      technician_id: parseInt(this.state.appointment.technician_id),
      doctor_id: parseInt(this.state.appointment.doctor_id),
    };
    this.state.isLoading = true;
    const method = appointment.id ? "put" : "post";
    ApiService.call(appointmentUrls.crud, appointment, method)
      .then(() => {
        utils.hideForm("scheduleFormModal");
        if (this.props.onFetch) {
          this.props.onFetch();
        }
        this.resetForm();
        this.state.isLoading = false;
      })
      .catch(() => {
        this.state.isLoading = false;
      });
  }
  resetForm() {
    this.state.appointment = { ...this.state.defaultAppointment };
    this.state.filterTimeSlot = {};
    this.state.technicianList = [];
    this.state.doctorList = [];
    this.state.technicians = [];
    this.state.doctors = [];
    this.resetTimeSlot();
    this.customerFormRef.initForm();
  }
  onSelectBookingType(value, isChangePlace = false) {
    if ((value == this.state.appointment.booking_type || !this.state.isNotYetOccurred) && !isChangePlace) {
      return;
    }
    this.handleOnChange("booking_type");
    this.state.appointment.doctor_id = "";
    this.state.appointment.technician_id = "";
    this.state.appointment.booking_date = "";
    this.resetTimeSlot();
    if (this.state.isEdit && this.state._appointment.booking_type == value) {
      this.state.appointment = { ...this.state._appointment };
      this.state.isInitEdit = true;
    }
    this.state.appointment.booking_type = value;
  }

  resetSelectDoctorAndTechnician() {
    switch (parseInt(this.state.appointment.booking_type)) {
      case this.bookingType.dateTime:
        this.state.appointment.doctor_id = "";
        this.state.appointment.technician_id = "";
        break;
      case this.bookingType.doctor:
        this.state.appointment.technician_id = "";

        break;
      case this.bookingType.technician:
        this.state.appointment.doctor_id = "";
        break;
    }
  }
  async getTimeSlot() {
    try {
      this.state.isFetching = true;
      const res = await ApiService.call(timeSlotUrls.crud, this.state.filterTimeSlot, "get");
      const overbook = this.state._appointment?.overbook;
      const overbookTimeSlots = res.filter((x) => {
        return (
          (x.booked && x.id != this.state._appointment?.time_slot_id) ||
          (overbook && x.id == this.state._appointment?.time_slot_id)
        );
      });

      this.state.overbookTimeSlots = overbookTimeSlots;
      const timeSlots = res.filter((x) => {
        return (
          (!x.booked && x.id != this.state._appointment?.time_slot_id) ||
          (!overbook && x.id == this.state._appointment?.time_slot_id)
        );
      });

      this.state.timeSlots = timeSlots;

      const formatTimeSlot = (timeSlots) => {
        const slots = timeSlots.filter((timeSlot) => {
          const { enable, examination_date, start_time } = timeSlot;
          const slotDateTime = this.toDateTime(examination_date, start_time);
          return slotDateTime.isAfter(new Date()) && enable;
        });
        return slots.reduce((arr, timeSlot) => {
          let existingGroup = arr.find((item) => item.start_time === timeSlot.start_time);
          if (existingGroup) {
            existingGroup.data.push(timeSlot);
            existingGroup.ids.push(timeSlot.id);
          } else {
            arr.push({ start_time: timeSlot.start_time, data: [timeSlot], ids: [timeSlot.id] });
          }
          return arr;
        }, []);
      };

      this.state.times = formatTimeSlot(timeSlots);
      this.state.overbookTimes = formatTimeSlot(overbookTimeSlots);
      this.state.isFetching = false;
    } catch (err) {
      this.state.isFetching = false;
    }
  }

  onSelectDate(value) {
    let date = "";
    if (typeof value === "string") {
      date = value;
    } else if (typeof value === DateTime) {
      date = utils.dateToYYYYMMDD(value.toJSDate());
    }
    this.state.appointment.overbook = false;
    this.state.appointment.booking_date = date;
    this.handleOnChange("booking_date");
  }
  getListPlace() {
    ApiService.call(placeUrls.crud, {}, "get").then((res) => {
      this.state.places = res;
    });
  }
  getListEmployee(params = {}) {
    this.handleGetEmployee(params).then((res) => {
      this.state.technicians = res.filter((item) => !item.is_doctor);
      this.state.doctors = res.filter((item) => item.is_doctor);
    });
  }

  handleGetEmployee(params = {}) {
    return ApiService.call(employeeUrls.getListDoctorAndTechnician, params, "get");
  }
  handleOnChange(key, isResetTime = true) {
    this.state.error[key] = "";
    if (isResetTime) this.state.appointment.booking_time = "";
  }
  validAppointmentForm() {
    const { doctor_id, time_slot_id, type, technician_id, booking_date, booking_type, booking_time } =
      this.state.appointment;
    this.state.error = {
      ...this.state.error,
      booking_date: validators.commonValidate(booking_date, "ngày khám mong muốn"),
      booking_time: validators.validateSelectOption(booking_time, "giờ khám mong muốn"),
      doctor_id: validators.validateSelectOption(doctor_id, "bác sĩ"),
      type: validators.validateSelectOption(type, "loại lịch"),
      time_slot_id: time_slot_id ? "" : "time_slot_id",
    };
    if (booking_type == this.bookingType.technician) {
      this.state.error.technician_id = validators.validateSelectOption(technician_id, "kỹ thuật viên");
    }
    return utils.checkEmptyKeys(this.state.error);
  }

  toDateTime(date, time) {
    return moment(`${date} ${time}`, "YYYY-MM-DD hh:mm");
  }
  onSelectTimeSlot(time) {
    this.state.error.booking_time = "";
    this.state.appointment.booking_time = time.start_time;
  }
  getActiveTimeSlot(time) {
    return (
      time.ids.includes(this.state.appointment.time_slot_id) ||
      (this.bookingType.dateTime == this.state.appointment.booking_type &&
        this.state.appointment.booking_time == time.start_time)
    );
  }
  checkDisabledMoreInfoAppointment() {
    return !(
      this.state.appointment.time_slot_id ||
      (this.bookingType.dateTime == this.state.appointment.booking_type && this.state.appointment.booking_time)
    );
  }
  isNotHaveTimeSlot(key) {
    const slotDateTime = this.toDateTime(this.state.appointment.booking_date, this.state.appointment.booking_time);
    const arr = this.state.appointment.overbook ? this.state.overbookTimes : this.state.times;
    const value = this.state.appointment[key];
    return (value || (!key && this.bookingType.dateTime == this.state.appointment.booking_type)) &&
      this.state.appointment.booking_date &&
      (!this.state.isEdit || slotDateTime.isAfter(new Date()))
      ? !arr.length
      : false;
  }
  get isDisableInputDate() {
    const { doctor_id, technician_id, booking_type } = this.state.appointment;
    return (
      (!doctor_id && booking_type == this.bookingType.doctor) ||
      (booking_type == this.bookingType.technician && !technician_id) ||
      !this.state.canEdit
    );
  }
  checkDisabledOverbook() {
    const times = this.state.times.map((x) => x.start_time);
    const overbookTimes = this.state.overbookTimes.map((x) => x.start_time);
    return !overbookTimes.some((x) => !times.includes(x));
  }
}

ScheduleForm.components = { CustomDatePicker, CustomerForm };
ScheduleForm.defaultProps = {
  onFetch: () => {},
  appointment: {},
  date: "",
  time: "",
};
ScheduleForm.template = "z_appointment.ScheduleForm";
