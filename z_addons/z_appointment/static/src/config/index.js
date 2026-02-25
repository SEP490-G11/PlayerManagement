/** @odoo-module **/
import { ApiService } from "@z_web/services/api_service";

const urlMap = {
  appointment: {
    prefix: "z_appointment/appointment",
    endpoints: {
      crud: "",
      updateState: "update_state",
      exportExcel: "export_excel",
      updatePrintingType: "update_printing_type",
    },
  },
  employee: {
    prefix: "z_hr/employee",
    endpoints: {
      getListDoctorAndTechnician: "get_list_doctor_and_technician",
    },
  },
  customer: {
    prefix: "z_partner/customer",
    endpoints: {
      crud: "",
    },
  },
  group: {
    prefix: "z_partner/group",
    endpoints: {
      crud: "",
    },
  },
  timeSlot: {
    prefix: "z_hr/timeslots",
    endpoints: {
      crud: "",
      getSlotsWithDoctorWorking: "get_slots_with_doctor_working",
    },
  },
  place: {
    prefix: "z_place/places",
    endpoints: {
      crud: "",
    }

  }
};
export const appointmentUrls = ApiService.prefixMapValues(urlMap.appointment);
export const employeeUrls = ApiService.prefixMapValues(urlMap.employee);
export const customerUrls = ApiService.prefixMapValues(urlMap.customer);
export const timeSlotUrls = ApiService.prefixMapValues(urlMap.timeSlot);
export const groupCustomerUrls = ApiService.prefixMapValues(urlMap.group);
export const placeUrls = ApiService.prefixMapValues(urlMap.place)
