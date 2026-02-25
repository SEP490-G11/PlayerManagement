/** @odoo-module **/

const { Component, useState, onWillStart, onMounted, markup } = owl;
import { registry } from "@web/core/registry";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { ScheduleForm } from "../schedule_form/schedule_form";
import { ApiService } from "@z_web/services/api_service";
import { timeSlotUrls, appointmentUrls, placeUrls } from "../../config";
import { SharedComponent } from "@z_web/shared";
import { models, appointmentStatusOptions } from "@z_web/constants";
import utils from "@z_web/utils";
import { _t } from "@web/core/l10n/translation";

export class ScheduleCalendar extends Component {
  setup() {
    this.formRef = null;
    this.propsConfirm = {
      title: _t("Are you sure you want to delete the appointment?"),
      content: _t("Note: All appointment information will be deleted from the system."),
    };
    this.state = useState({
      activeId: false,
      isLoading: false,
      place: {},
      listWorkingDays: [],
      today: new Date(),
      dateOfWeeks: [],
      dateLabelList: [],
      selectedDate: new Date(),
      rangeCurrentWeek: "",
      listQuantityOfAppointmentsPerDay: [],
      appointmentList: [],
      places: [],
      activeAppointment: false,
      queryParams: {},
      timeArray: {},
      isShowPopover: false,
      statusList: appointmentStatusOptions,
    });
    this.currentTime = new Date();

    onWillStart(async () => {
      await this.getCurrentWeekDays();
      await this.getListPlace();
      this.state.place = this.state.places[0] ?? { name: "", id: 0,}
      this.state.queryParams.place_id = this.state.place.id
    });
    onMounted(async () => {
      this.selectDate(new Date());
      this.formRef = utils.getChildComponent(this, "ScheduleForm");
      setTimeout(() => {
        this.scrollIntoCurrentTime();
      }, 1000);
    });

    this.appointmentModel = models.appointment;
  }

  async getWorkingDays(startDate, endDate, place ) {
    const res = await ApiService.call(timeSlotUrls.getSlotsWithDoctorWorking, { startDate, endDate, place_id :place }, "get");
    if (res) {
      this.state.listWorkingDays = res;
    }
  }

  async getListPlace() {
    const res = await ApiService.call(placeUrls.crud, {}, "get")
    this.state.places = res ;
  }

  // Trigger popover
  selectAppointment(event, item) {
    if (item) {
      this.state.popoverHeaderLabel = this.dateToStringPopoverHeader(item);
      this.state.isShowPopover = true;
      // Compute axis
      const axisX = event.pageY + 30 < 100 ? 250 : event.pageX + 30;
      const axisY = event.pageY + 150 > window.innerHeight ? window.innerHeight - 170 : event.pageY;
      // setTimeout(() => {
      $("#appointment-preview").css("top", axisY + 30 + "px");
      $("#appointment-preview").css("left", axisX - 220 + "px");
      $("#appointment-preview").removeClass("hide");
      $("#appointment-preview").addClass("show");
      this.state.activeAppointment = item;
      // }, 100)
    } else {
      this.state.activeAppointment = false;
      this.state.isShowPopover = false;
      $("#appointment-preview").addClass("hide");
      $("#appointment-preview").removeClass("show");
    }
  }

  // Generate object include working time time for 1 day

  // From 7:30 to 19:00
  generateArrayTime() {
    let array = {};
    for (let hour = 0; hour < 24; hour++) {
      let correctHour = hour < 10 ? "0" + hour : hour;
      for (let minute = 0; minute <= 45; minute += 15) {
        if (!(hour === 24 && (minute === 0 || minute === 15))) {
          let correctMinute = minute < 10 ? "0" + minute : minute;
          let element = `${correctHour}:${correctMinute}`;
          for (let i = 0; i < this.state.dateOfWeeks.length; i++) {
            const item = this.state.dateOfWeeks[i];
            if (!array[element]) {
              array[element] = {};
            }
            array[element][utils.formatDate(item)] = [];
          }
        }
      }
    }
    return array;
  }

  // Call api get appoiment
  async fetchAppointments() {
    this.state.listQuantityOfAppointmentsPerDay = this.state.dateOfWeeks.map((item) => {
      return {
        label: utils.dateToYYYYMMDD(item),
        overbook: 0,
        normal: 0,
      };
    });

    const res = await ApiService.call(appointmentUrls.crud, { ...this.state.queryParams, is_not_paging: 1 }, "get");
    let array = this.generateArrayTime();
    const result = res;
    if (result.length != 0) {
      const itemList = result.sort((a, b) => (a.booking_time > b.booking_time ? 1 : -1));

      for (let i = 0; i < itemList.length; i++) {
        // Map status
        const appointment = itemList[i];
        const stt = this.state.statusList.find((stt) => stt.value == appointment.status);
        appointment.status = stt?.label;
        // Count overbook and normal
        const findDay = this.state.listQuantityOfAppointmentsPerDay.filter((item) => {
          return item.label == appointment.booking_date;
        });
        if (findDay && findDay.length == 0) {
          let newItem = {};
          if (appointment.overbook) {
            newItem = { overbook: 1, normal: 0 };
          } else {
            newItem = { overbook: 0, normal: 1 };
          }
          newItem.label = appointment.booking_date;
          this.state.listQuantityOfAppointmentsPerDay = [...this.state.listQuantityOfAppointmentsPerDay, newItem];
        } else {
          this.state.listQuantityOfAppointmentsPerDay = this.state.listQuantityOfAppointmentsPerDay
            .map((item) => {
              if (item.label == appointment.booking_date) {
                if (appointment.overbook) {
                  item.overbook = item.overbook + 1;
                } else {
                  item.normal = item.normal + 1;
                }
              }
              return item;
            })
            .filter((it) => it);
        }

        // End count overbook and normal schedule
        // Convert appoinemnt list to table data
        if (!array[appointment.booking_time][appointment.booking_date]) {
          array[appointment.booking_time][appointment.booking_date] = [appointment];
        } else if (array[appointment.booking_time][appointment.booking_date]) {
          array[appointment.booking_time][appointment.booking_date] = [
            ...array[appointment.booking_time][appointment.booking_date],
            appointment,
          ];
        }
        array[appointment.booking_time][appointment.booking_date].sort((a, b) => {
          return a.overbook - b.overbook;
        });
      }

      this.state.timeArray = array;
    } else {
      let array = this.generateArrayTime();
      this.state.timeArray = array;
      this.state.appointmentList = false;
    }
    this.state.queryParams = { ...this.state.queryParams };
  }

  checkAvailableTime(time, date) {
    let isAvailable = false;
    for (let i = 0; i < this.state.listWorkingDays.length; i++) {
      const bookingDate = this.state.listWorkingDays[i].booking_date;
      if (bookingDate === date) {
        isAvailable = this.state.listWorkingDays[i].booking_time.includes(time);
        break;
      }
    }
    return isAvailable;
  }

  handleClassNameForCell(time, date) {
    let className = "";
    const isAvailable = this.checkAvailableTime(time, date);
    const isPast = this.checkEnableAddAppointment(time, date);
    if (this.state.timeArray[time][date] && this.state.timeArray[time][date].length > 0) {
      return "";
    }
    if (!isAvailable) {
      className = className + " empty-cell";
    } else if (!isPast) {
      className = className + "timeslot-disable";
    }
    return className;
  }

  // On edit schedule
  editAppointment() {
    const appointment = this.state.activeAppointment;
    this.state.activeAppointment = false;
    this.state.activeAppointment = appointment;
    this.formRef.openModal(appointment);
    this.hidePopover();
  }

  hidePopover() {
    $("#appointment-preview").addClass("hide");
    $("#appointment-preview").removeClass("show");
  }

  // Map week data to table
  // Handle get all days and params of current week display in calendar
  // After that call api get list appointment by params
  async mapAppointmentToTable(daysOfWeek) {
    this.hidePopover();
    if (daysOfWeek) {
      const firstDayOfWeek = daysOfWeek[0];
      const lastDayOfWeek = daysOfWeek[daysOfWeek.length - 1];
      this.state.dateLabelList = [];
      for (let i = 0; i < daysOfWeek.length; i++) {
        const day = daysOfWeek[i];
        this.state.dateLabelList = [...this.state.dateLabelList, utils.dateToYYYYMMDD(day)];
      }
      const start_date = utils.dateToYYYYMMDD(firstDayOfWeek);
      const end_date = utils.dateToYYYYMMDD(lastDayOfWeek);
      this.state.queryParams.start_date = start_date;
      this.state.queryParams.end_date = end_date;
      this.state.dateOfWeeks = daysOfWeek;
      await this.getWorkingDays(start_date, end_date, this.state.place.id);

      await this.fetchAppointments();
    }
  }

  // Get current weeks by current days
  //return [ DateTime ] list date time of current week
  async getCurrentWeekDays() {
    this.state.dateOfWeeks = utils.getCurrentWeekDays(this.state.selectedDate);
  }

  // Get week range to return string to display in lable canlendar title
  // Example : 22/02/2021 - 28/02/2021
  getWeekRange() {
    const lastIndex = this.state.dateOfWeeks.length - 1;
    const firstDate = this.state.dateOfWeeks[0];
    const lastDate = this.state.dateOfWeeks[lastIndex];
    // check first date and last date of week is null or not
    if (firstDate && lastDate) {
      return `${utils.formatDate(firstDate)}  - ${utils.formatDate(lastDate)}`;
    }
    return "";
  }

  // Convert date to popover header
  dateToStringPopoverHeader(appointment) {
    if (appointment) {
      const { booking_date, booking_time } = appointment;
      const dateParts = booking_date.split("-");
      let date = utils.YYYYMMDDToDate(booking_date);
      return `${this.getLabelByDate(date)}, ${dateParts[2]}/${dateParts[1]} | ${this.convertTimeToRangeTime(
        booking_time
      )}`;
    }
  }

  getLabelByDate(date) {
    switch (date.getDay()) {
      case 0:
        return _t("Sunday");
      case 1:
        return _t("Monday");
      case 2:
        return _t("Tuesday");
      case 3:
        return _t("Wednesday");
      case 4:
        return _t("Thursday");
      case 5:
        return _t("Friday");
      case 6:
        return _t("Saturday");
      default:
        return _t("Sunday");
    }
  }

  // On remove schedule
  onRemoveSchedule(appoiment) {
    this.state.activeId = appoiment.id;
  }

  async removeAppointment() {
    ApiService.call(appointmentUrls.crud + this.state.activeId, {}, "delete")
      .then(() => {
        $("#appointment-preview").addClass("hide");
        $("#appointment-preview").removeClass("show");
        this.state.activeAppointment = false;
        this.mapAppointmentToTable(this.state.dateOfWeeks);
        $("#remove-confirm-modal").modal("toggle");
      })
      .finally(() => {});
  }

  // Go to previous week
  goToForwardWeek() {
    this.state.dateOfWeeks = this.state.dateOfWeeks.map((item) => {
      return new Date(item.getTime() + 24 * 60 * 60 * 1000 * 7);
    });

    this.updateInputRangeDate();
  }

  backToPreviousWeekCalendar() {
    this.state.dateOfWeeks = this.state.dateOfWeeks.map((item) => {
      return new Date(item.getTime() - 24 * 60 * 60 * 1000 * 7);
    });

    this.updateInputRangeDate();
  }

  async updateInputRangeDate() {
    this.state.rangeCurrentWeek = this.getWeekRange();
    $("#2023123").text(this.state.rangeCurrentWeek);
    $("#2023124").text(this.state.rangeCurrentWeek);
    await this.mapAppointmentToTable(this.state.dateOfWeeks);
  }

  selectDate(value) {
    this.state.selectedDate = new Date(value);
    this.getCurrentWeekDays();
    this.updateInputRangeDate();
  }

  async selectPlace(value){
    this.state.place = value
    this.state.queryParams.place_id = value.id;
    await this.getWorkingDays(this.state.queryParams.start_date, this.state.queryParams.end_date , this.state.place.id);
    this.fetchAppointments()
  }

  getDateString(date) {
    return utils.formatDate(date);
  }

  // On create schedule form by date time
  onCreateByDateAndTime(date = "", time = "") {
    this.state.activeAppointment = false;
    const { place } = this.state;
    $("#appointment-preview").addClass("hide");
    $("#appointment-preview").removeClass("show");
    this.formRef.openModal(null, date, time, place.id);
  }

  convertTimeToRangeTime(time) {
    if (time) {
      const [hour, minute] = time.split(":");
      let numberHour = parseInt(hour, 10);
      let numberMinute = parseInt(minute, 10);

      if (numberMinute === 45) {
        numberMinute = 0;
        numberHour = numberHour + 1;
      } else {
        numberMinute = numberMinute + 15;
      }
      return `${time} - ${numberHour.toString().padStart(2, "0")}:${numberMinute.toString().padStart(2, "0")}`;
    }
    return "";
  } //

  checkEnableAddAppointment(time, date) {
    if (time && date) {
      const dateString = date + " " + time;
      const dateObj = utils.YYYYMMDDToDate(dateString);
      return this.currentTime.getTime() < dateObj.getTime();
    }
    return true;
  }
  getLabelDoctor(name) {
    return markup(_t("Dr.") + " " + `<span style='font-weight: 400'>${name}</span>`);
  }

  getLabelTechnician(name) {
    return markup(_t("TC.") + " " + `<span style='font-weight: 400'>${name}</span>`);
  }

  genIdbyTime(time) {
    // #replace : with -
    return time.replace(":", "-");
  }

  // #this function tranform current time to string format ex: 10:22 into 10-30
  scrollIntoCurrentTime() {
    const currentHour = this.currentTime.getHours();
    const currentMinute = this.currentTime.getMinutes();

    // Xác định phút được làm tròn
    let roundedMinute;
    if (currentMinute < 15) {
        roundedMinute = "00"; // Làm tròn xuống
    } else if (currentMinute < 30) {
        roundedMinute = "15"; // Làm tròn lên 15
    } else if (currentMinute < 45) {
        roundedMinute = "30"; // Làm tròn lên 30
    } else {
        roundedMinute = "45"; // Làm tròn lên 45
    }

    const currentHourString = currentHour < 10 ? "0" + currentHour : currentHour;
    const currentTimeString = `${currentHourString}-${roundedMinute}`;
    const row = document.getElementById(this.genIdbyTime(currentTimeString));
    if (row) {
        row.scrollIntoView({ behavior: "smooth", block: "start" });
    }
}
}

ScheduleCalendar.template = "z_appointment.ScheduleCalendar";
ScheduleCalendar.components = SharedComponent.appendComponents({
  Dropdown,
  DropdownItem,
  ScheduleForm,
});

registry.category("actions").add("zen8.action_schedule_calendar", ScheduleCalendar);
