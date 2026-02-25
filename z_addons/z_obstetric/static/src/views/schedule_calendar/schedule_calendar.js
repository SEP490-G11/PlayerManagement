/** @odoo-module */
import {patch} from "@web/core/utils/patch";


import {ScheduleCalendar} from "@z_appointment/views/schedule_calendar/schedule_calendar";
import utils from "@z_web/utils";



patch(ScheduleCalendar.prototype, {
     // From 0:00 to 23:45
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

});