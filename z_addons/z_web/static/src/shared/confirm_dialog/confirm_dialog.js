/** @odoo-module **/
const { Component } = owl;

export class ConfirmDialog extends Component {
  static props = {
    id: String,
    title: String,
    content: String,
    slots: { type: Object, optional: true },
  };
}

ConfirmDialog.template = "z_web.ConfirmDialog";
