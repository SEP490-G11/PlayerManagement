/** @odoo-module **/
import { ListController } from "@web/views/list/list_controller";

export class CustomModalController extends ListController {
  setup() {
    super.setup();
    this._setupModal();
  }

  _setupModal() {
    const modalHTML = `
            <div class="modal fade" id="confirmStatusScheduleModal" aria-labelledby="scheduleConfirmModalLabel" aria-hidden="true" data-bs-backdrop="static">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h1>Xác nhận kết thúc</h1>
                    </div>
                    <div class="modal-body form" style="background-color:#ebebeb">
                      Bạn có chắc chắn muốn kết thúc lượt khám này không?
                    </div>
                    <div class="modal-footer">
                        <button type="button" data-bs-dismiss="modal" class="btn btn-secondary cancel me-1">Hủy</button>
                        <button type="button" class="btn btn-primary save">Lưu lại</button>
                    </div>
                </div>
            </div>
        </div>
        `;

    if (!document.getElementById("confirmStatusScheduleModal")) {
      document.body.insertAdjacentHTML("beforeend", modalHTML);
    }
  }

  openModal(value) {
    this.value = value;
    this.modalElement = document.getElementById("confirmStatusScheduleModal");
    // Remove existing event listeners
    const saveButton = this.modalElement.querySelector(".save");
    const cancelButton = this.modalElement.querySelector(".cancel");
    saveButton.removeEventListener("click", this._handleSaveArrow);
    cancelButton.removeEventListener("click", this._handleCloseArrow);

    // Add new event listeners
    saveButton.addEventListener("click", this._handleSaveArrow);
    cancelButton.addEventListener("click", this._handleCloseArrow);

    $("#confirmStatusScheduleModal").modal("show");
  }

  closeModal() {
    $("#confirmStatusScheduleModal").modal("hide");
    const saveButton = this.modalElement.querySelector(".save");
    const cancelButton = this.modalElement.querySelector(".cancel");
    
    saveButton.removeEventListener("click", this._handleSaveArrow);
    cancelButton.removeEventListener("click", this._handleCloseArrow);
  }

  _handleSaveArrow = () => {
    this.props.onSave({ state: this.value });
    this.closeModal();
  };

  _handleCloseArrow = () => {
    this.closeModal();
  };
}
