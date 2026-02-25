/** @odoo-module */
import {patch} from "@web/core/utils/patch";
import {ScheduleForm} from "@z_appointment/views/schedule_form/schedule_form";
import {ApiService} from "@z_web/services/api_service";
import {appointmentUrls} from "@z_appointment/config";
import { appointmentState, appointmentApproachChannels } from "../../constants";
import utils from "@z_web/utils";
import { _t } from "@web/core/l10n/translation";

patch(ScheduleForm.prototype, {
    setup() {
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
            approach_channel: "1"
          };
        super.setup()
        this.state.appointment = {... appointment};
        this.state.defaultAppointment = {... appointment};
        this.typeAppointments = [
            { value: this.bookingType.dateTime, label: _t("Date time"), icon: "/z_web/static/image/grey-calander.svg" },
            { value: this.bookingType.doctor, label: _t("Doctor"), icon: "/z_web/static/image/doctor.svg" },
            { value: this.bookingType.technician, label: _t("Ultrasonographer"), icon: "/z_web/static/image/technician.svg" },
        ];
        this.appointmentApproachChannels = appointmentApproachChannels;

        useEffect(
          () => {
            const { booking_date, booking_time, doctor_id, technician_id, booking_type, overbook } = this.state.appointment;
            const arr = overbook ? this.state.overbookTimeSlots : this.state.timeSlots;
            if (doctor_id && technician_id && booking_type != 3) {
              this.state.appointment.time_slot_id =
                arr.find(
                  (x) =>
                    x.employee_id == doctor_id &&
                    this.toDateTime(x.examination_date, x.start_time).isSame(moment(`${booking_date} ${booking_time}`))
                )?.id || "";
            } else if (doctor_id && technician_id && booking_type == 3) {
              this.state.appointment.time_slot_id =
                arr.find(
                  (x) =>
                    x.employee_id == technician_id &&
                    this.toDateTime(x.examination_date, x.start_time).isSame(moment(`${booking_date} ${booking_time}`))
                )?.id || "";
            } else {
              this.state.appointment.time_slot_id =
                arr.find(
                  (x) =>
                    (x.employee_id == technician_id || x.employee_id == doctor_id) &&
                    this.toDateTime(x.examination_date, x.start_time).isSame(moment(`${booking_date} ${booking_time}`))
                )?.id || "";
            }
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
    },

    
  

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
          group_id: customer.group_id ? customer.group_id : null,
          street: customer.street.trim(),
          name: customer.name.trim(),
          date: customer.date.trim(),
          gender: customer.gender.trim(),
          mobile: customer.mobile.trim(),
          job: (typeof customer.job === "string" ? customer.job : "").trim(),
          is_customer: true,
        },
      },
      booking_type: `${this.state.appointment.booking_type}`,
      time_slot_id: parseInt(this.state.appointment.time_slot_id),
      technician_id: parseInt(this.state.appointment.technician_id),
      doctor_id: parseInt(this.state.appointment.doctor_id),
      date_assign: utils.dateToYYYYMMDD(new Date()),
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
  },

  validAppointmentForm() {
    const { time_slot_id, type, technician_id, booking_date, booking_type, booking_time, doctor_id } =
      this.state.appointment;
    this.state.error = {
      ...this.state.error,
      booking_date: validators.commonValidate(booking_date, "ngày khám mong muốn"),
      booking_time: validators.validateSelectOption(booking_time, "giờ khám mong muốn"),
      type: validators.validateSelectOption(type, "loại lịch"),
      time_slot_id: time_slot_id ? "" : "time_slot_id",
    };
    if (booking_type == this.bookingType.technician) {
      this.state.error.technician_id = validators.validateSelectOption(technician_id, "kỹ thuật viên");
      this.state.error.doctor_id = null;
    }
    if (!technician_id && !doctor_id) {
      const _error = {
        success: false,
        code: 400,
        message: _t("Need choose doctor or technician"),
        isShowToast: true,
      };
      utils.showToast(_error);
    }
    return utils.checkEmptyKeys(this.state.error);
  },
});
