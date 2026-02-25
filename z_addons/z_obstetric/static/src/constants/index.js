/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
export const appointmentState = {
  NOT_YET_ARRIVED: "1",
  WAITING: "2",
  EXAMINING: "3",
  WAITING_FOR_ULTRASOUND: "4",
  RESULT_SA: "5",
  RESULT_TEST: "6",
  WAITING_FOR_CONCLUDE: "7",
  CONCLUDED_REGISTER_TIP: "8",
  FINISHED: "9",
  WAITING_FOR_TIP: "10",
  DOING_TIP: "11",
  FINISHED_TIP: "12"
};

export const appointmentApproachChannels = [
  {
    value: "1",
    label: _t("Ads"),
  },
  {
    value: "2",
    label: _t("No ads"),
  },
]

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
    label: _t("Waiting for ultrasound"),
  },
  {
    value: "5",
    label: _t("Result SA"),
  },
  {
    value: "6",
    label: _t("Result test"),
  },
  {
    value: "7",
    label: _t("Waiting for conclude"),
  },
  {
    value: "8",
    label: _t("Concluded and register tip"),
  },
  {
    value: "9",
    label: _t("Finished"),
  },
  {
    value: "10",
    label: _t("Waiting for tip"),
  },
  {
    value: "11",
    label: _t("Doing tip"),
  },
  {
    value: "12",
    label: _t("Finished tip"),
  },
];

export const obstetricsContactOptions = [
  {
    value: "1",
    label: "Facebook",
  },
  {
    value: "2",
    label: "Hotline",
  },
  {
    value: "3",
    label: "Zalo",
  },
  {
    value: "4",
    label: "Website",
  },
  {
    value: "5",
    label: "Tiktok",
  },
  {
    value: "6",
    label: "Instagram",
  },
  {
    value: "7",
    label: "Thread",
  },
  {
    value: "8",
    label: _t("Flyer"),
  },
  {
    value: "9",
    label: "Standee",
  },
  {
    value: "10",
    label: _t("Self-coming"),
  },
  {
    value: "11",
    label: _t("Other"),
  },
];
