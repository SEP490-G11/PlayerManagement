/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
const { Component, useState, onWillStart, useEffect, EventBus } = owl;
import { useService } from "@web/core/utils/hooks";
import utils from "@z_web/utils/toast";
import { PayOSCheckout } from './payos-initialize';

export class CreateQRAccountPayment extends Component {
  setup() {
    this.data = this.props;
    this.orm = useService("orm");
    this.action = useService("action");
    this.notification = useService("notification");
    this.invoice_amount = this.data.action.context.amount;
    this.state = useState({
      isGotQR: false,
      paymentQRId: null,
      amount: 0,
      current_id: 0,
      isLoading: false,
      isPaid: false,
      transactionId: null,
      error:{},
      formatAmount: this.formatAmount(this.data.action.context.amount),
      bin: "",
      transactionCode: "",
      callbackCancel: null,
      customInput: "",
      paymentLink: "",
      payOSConfig: {
        RETURN_URL: this.data.action.context.return_url,
        ELEMENT_ID: "iframe-qr-zen9",
        CHECKOUT_URL: "",
        embedded: true,
        onSuccess: (event) => {
            this.onSuccess()
        },
        onCancel: (event) => {
          //#TODO: handle cancel payment
        },
        onExit: (event) => {
          //#TODO: handle exit payment
        },
      },
    });

    onWillStart(async () => {
      this.state.amount = this.data.action.context.amount;
      this.state.current_id = this.data.action.context.current;
      this.state.transactionCode = this.generateTransactionCode(
        this.data.action.context.code,
        this.data.action.context.current
      );
    });
  }

  async createPaymentQR() {
    if(this.validateAmount()){
      this.state.isLoading = true;
    try {
      const paymentLinkData = await this.orm.call("account.payment", "create_vietqr", [
        [this.data.action.context.active_id],
        this.state.amount,
        this.state.transactionCode,
      ]);
      this.state.current_id = this.state.current_id + 1;
      if (paymentLinkData) {
          const checkoutUrl = paymentLinkData.checkout_url;
          this.state.payOSConfig.CHECKOUT_URL = checkoutUrl;
          const { open, exit } = PayOSCheckout.usePayOS(this.state.payOSConfig);
          await open();
          this.state.paymentQRId = paymentLinkData.qr_payment_id;
          this.state.callbackCancel = exit;
          this.state.bin = paymentLinkData.bin;
          this.state.isGotQR = true;
        }
      } catch (error) {
        utils.showToast(
          this.notification,
          utils.state.error,
          utils.type.error,
          "",
          "",
          "Có lỗi xảy ra khi tạo link thanh toán QR. Vui lòng thử lại sau."
        );
      }
      this.state.isLoading = false;
    }
  }

  generateTransactionCode(code, current) {
    return code + "/" + "QR" + (current + 1).toString().padStart(2, "0");
  }

  async onSuccess() {
    try {
      const action = await this.orm.call(
        "z_payos.qr.logs",
        "pay_qr_payment",
        [[this.state.paymentQRId]],
        {}
      );

      await this.orm.call("account.payment", "action_vietqr_post", [
        [this.data.action.context.active_id],
        this.state.bin,
        this.state.paymentQRId,
      ], {});

      // Show success notification
      utils.showToast(
        this.notification,
        utils.state.success,
        utils.type.success,
        "",
        "",
        "Thanh toán thành công!"
      );

      // Close the wizard
      this.action.doAction({ type: "ir.actions.act_window_close" });

    } catch (error) {
      utils.showToast(
        this.notification,
        utils.state.error,
        utils.type.error,
        "",
        "",
        "Có lỗi xảy ra khi xử lý thanh toán. Vui lòng thử lại sau."
      );
    }
    this.state.isPaid = true;
  }

  async onClickCancel(e) {
    e.preventDefault();
    this.state.isPaid = false;
    this.state.isGotQR = false;
    this.state.transactionCode = this.generateTransactionCode(this.data.action.context.code, this.state.current_id);
    this.state.callbackCancel && this.state.callbackCancel();
    await this.orm.call("z_payos.qr.logs", "cancel_qr_payment", [[this.state.paymentQRId]], {});
  }

  validateAmount() {
    if (this.state.amount <= 0) {
      this.state.error.amount = _t("Số tiền thanh toán phải lớn hơn 0");
      return false;
    }
    if (this.state.amount > this.invoice_amount) {
      this.state.error.amount = _t("Số tiền thanh toán không được vượt quá số tiền hóa đơn");
      return false;
    }
    return true;
  }

  onChangeAmount(e) {
    this.state.error.amount = "";
    const amount = e.target.value;
    this.state.amount = parseInt(amount.replace(/\D/g, "") || 0);
    this.state.formatAmount = this.formatAmount(this.state.amount);
  }

  formatAmount(amount) {
    return amount.toLocaleString("de-DE");
  }

  async showQrCounter(e) {
    const action = await this.orm.call(
      "account.move",
      "show_qr_into_counter",
      [[this.data.action.context.active_id], this.state.payOSConfig.CHECKOUT_URL],
      {}
    );
  }
}


CreateQRAccountPayment.template = "z_payos.CreateQRAccountPayment";

export const createQRAccountPayment = {
  component: CreateQRAccountPayment,
};

registry.category("actions").add("z_payos.create_qr_account_payment", CreateQRAccountPayment);
