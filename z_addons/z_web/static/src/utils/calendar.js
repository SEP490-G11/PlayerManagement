
/** @odoo-module **/


export default {
    //Get first monday of current week
  getMondayOfCurrentWeek(date, firstDayOfWeekIndex = 1) {
    const dayOfWeek = date.getDay(),
      firstDayOfWeek = new Date(date),
      diff = dayOfWeek >= firstDayOfWeekIndex ?
        dayOfWeek - firstDayOfWeekIndex :
        6 - dayOfWeek

    firstDayOfWeek.setDate(date.getDate() - diff)
    firstDayOfWeek.setHours(0, 0, 0, 0)

    return firstDayOfWeek
  },
  //
  getCurrentWeekDays(currentDate) {
    const currentWeekDays = [];
    const firstDayOfWeek = this.getMondayOfCurrentWeek(currentDate);
    for (let i = 0; i < 7; i++) {
      const currentDate = new Date(firstDayOfWeek);
      currentDate.setDate(firstDayOfWeek.getDate() + i);
      currentWeekDays.push(new Date(currentDate));
    }
    return currentWeekDays;
  }


  
};