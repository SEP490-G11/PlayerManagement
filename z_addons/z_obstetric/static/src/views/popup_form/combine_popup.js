/** @odoo-module **/
import { registry } from "@web/core/registry";
import { CustomModalController } from "./custom_popup_form";
import { AddHeaderName, AddHeaderNameRenderer } from "../../../../../z_medical_record/static/src/medical_record_tree/index";
import { listView } from "@web/views/list/list_view";

export const MedicalRecordTreeView = {
  ...listView,
  Controller: CustomModalController,
  ArchParser: AddHeaderName,
  Renderer: AddHeaderNameRenderer,
};

registry.category("views").add("combine_popup_record_tree", MedicalRecordTreeView);
