/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
export const appointmentState = {
  NOT_YET_ARRIVED: "1",
  WAITING: "2",
  EXAMINING: "3",
  CONSULT: "4",
  FINISHED: "5",
  WAITING_FOR_CONCLUDE: "6",
  CYCLOGYL: "7",
  SUBCLINICAL: "8",
  EXPIRED: "9",
};

export const appointmentStateOptions = [
  {
    value: "1",
    label: _t("Not Yet Arrived"),
  },
  {
    value: "2",
    label: _t("Waiting"),
  },
  {
    value: "3",
    label: _t("Examining"),
  },
  {
    value: "4",
    label: _t("Consult"),
  },
  {
    value: "5",
    label: _t("Finished"),
  },
  {
    value: "6",
    label: _t("Waiting for conclude"),
  },
  {
    value: "7",
    label: _t("Cyclogyl"),
  },
  {
    value: "8",
    label: _t("Subclinical"),
  },
  {
    value: "9",
    label: _t("Expired"),
  },
];

export const appointmentPrintingTypeOptions = [
  {
    value: "Vivision",
    label: _t("Vivision"),
  },
  {
    value: "Vivision Kid",
    label: _t("Vivision Kid"),
  },
]

export const floors = [
   {
    value:"0",
    label: "",
   },
  {
    value: "2",
    label: _t("2nd  Floor"),
  },
  {
    value: "3",
    label: _t("3nd Floor"),
  },
  {
    value: "4",
    label: _t("4th Floor"),
  },

]