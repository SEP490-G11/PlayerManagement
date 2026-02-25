/** @odoo-module **/

const prefix = "zen8.icare";

export const models = {
  modelAccess: "ir.model.access",
  company: "res.company",
  user: "res.users",
  userGroup: "res.groups",
  changePasswordWizard: "change.password.wizard",
  customer: "res.partner",
  customerGroup: `${prefix}.group`,
  employeeRole: `${prefix}.staff_role`,
  employee: `${prefix}.staff`,
  doctor: `${prefix}.doctor`,
  appointment: `${prefix}.appointment`,
  workingDay: `${prefix}.working_day`,
  timeSlot: `${prefix}.time_slot`,
  generalHealthExamination: `${prefix}.general_health_examination`,
  contactLensExamination: `${prefix}.contact_lens_examination`,
  contactLensReexamination: `${prefix}.contact_lens_reexamination`,
  binocularVisionExamination: `${prefix}.binocular_vision_examination`,
};

export const errorCodes = {
  duplicate: "DUPLICATE",
};
