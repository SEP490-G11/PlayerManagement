/** @odoo-module **/

const { Component, useState } = owl;

export class ConfirmStatusSchedule extends Component {
  setup() {
    this.state = useState({ isLoading: false, params: null });
  }

  openModal(open, params) {
    this.state.params = params;
    if (open) {
      $("#confirmStatusScheduleModal").modal("show");
    } else {
      $("#confirmStatusScheduleModal").modal("hide");
    }
  }

  save() {
    const { id, state, is_visit } = this.state.params;
    if (state) {
      this.props.onSave({ id: id, state: state, is_visit: is_visit });
      $("#confirmStatusScheduleModal").modal("hide");
      this.state.params = null;
    }
  }
}

ConfirmStatusSchedule.template = "z_obstetrics.ConfirmStatusSchedule";

