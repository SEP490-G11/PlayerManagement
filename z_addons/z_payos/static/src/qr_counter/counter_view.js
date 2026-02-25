/** @odoo-module **/
const { Component, useState, onWillStart, useRef, onMounted, useEffect } = owl;
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
import { Carousel } from "@z_web/shared/carousel/carousel";
export class QRCounter extends Component {
  setup() {
    this.eventReceiveQR = "notification.counter/qr_event";
    this.eventShowInvoice = "notification.counter/show_invoice_event";
    this.eventCancelQR = "notification.counter/cancel_qr_event";
    this.elementId = "iframe-counter-qr";
    this.counterViewRef = useRef("counterView");
    this.tableViewRef = useRef("invoiceTable");
    this.qrIframeRef = useRef("qrIframe");
    this.imgBannerList = [
      { id:1 , url: "https://www.circlek.com.vn/wp-content/uploads/2024/07/CFS-Matcha.jpg"},
      { id:2 , url: "https://napas.qltns.mediacdn.vn/thumb_w/960/479491956813160448/2024/10/2/1920x800-17278555813201523296343.jpg"},
      { id:3 , url: "https://www.circlek.com.vn/wp-content/uploads/2024/08/PHATEA-TRA-CHANH-THAI_Web-Banner_625x365px_R2.png"}
    ];
    this.orm = useService("orm");
    this.busService = this.env.services.bus_service;
    this.state = useState({
      invoiceLines: [],
      channel: "",
      isDone: false,
      imgBannerList: this.imgBannerList,
      checkoutUrl: null,
      isShowInvoice: false,
      isShowQR: false,
      cancelCallback: null,
      amount: 0,
      qrCodeImageUrl: "",
      payOSConfig: {
        RETURN_URL: null,
        ELEMENT_ID: this.elementId,
        CHECKOUT_URL: "",
        embedded: true,
        onSuccess: (event) => {
          this.onSuccess();
        },
        onCancel: (event) => {},
        onExit: (event) => {},
      },
    });

    onWillStart(async () => {
      await loadJS("https://cdn.payos.vn/payos-checkout/v1/stable/payos-initialize.js");
      this.initData();
    });

    useEffect(() => {
      let timeoutId;
      if (this.state.isShowQR) {
        timeoutId = setTimeout(() => {
          this.state.isShowQR = false;
        }, 60000);
      }
      return () => {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
      };
    }, () => [this.state.isShowQR]);


    useEffect(() => {
      let timeoutId;
      if (this.state.isShowInvoice) {
        timeoutId = setTimeout(() => {
          this.state.isShowInvoice = false;
        }, 60000);
      }
      return () => {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
      };
    }, () => [this.state.isShowInvoice]);


    useEffect(() => {
      const tableElement = this.tableViewRef.el;
      if (tableElement) {
        if (tableElement) {
          const startScroll = tableElement.scrollTop;
          const endScroll = tableElement.scrollHeight;
          const duration = 10000;
          let startTime;
  
          const scrollStep = (timestamp) => {
              if (!startTime) {
                  startTime = timestamp;
              }
              const progress = Math.min((timestamp - startTime) / duration, 1);
              const currentScroll = startScroll + progress * (endScroll - startScroll);
              tableElement.scrollTop = currentScroll;
  
              if (progress < 1) {
                  window.requestAnimationFrame(scrollStep); 
              }
          };
  
          window.requestAnimationFrame(scrollStep);
      } 
      }
  }, () => [this.state.invoiceLines]);

    onMounted(() => {
      this.hiddenElementView();
    });
  }

  onMessage({ detail: notifications }) {
    console.log("onMessage", notifications);
    const showQRNotifications = notifications.filter((item) => item.type === this.eventReceiveQR);
    const showInvoiceNotifications = notifications.filter((item) => item.type === this.eventShowInvoice);
    const cancelQRNotifications = notifications.filter((item) => item.type === this.eventCancelQR);

    for (const item of showQRNotifications) {
      this.handleShowQREvent(item.payload);
    }

    for (const item of showInvoiceNotifications) {
      this.handleShowInvoiceEvent(item.payload);
    }

    for (const item of cancelQRNotifications) {
      this.handleCancelQREvent();
    }
  }

  async handleShowQREvent(data) {
    if (
      data.checkout_url === this.state.payOSConfig.CHECKOUT_URL && 
      this.state.isShowQR
    ) {
      return;
    }
    this.removeQRIframeElement();
    Object.assign(this.state, {
      payOSConfig: {
        ...this.state.payOSConfig,
        CHECKOUT_URL: data.checkout_url,
      },
      invoiceLines: data.invoice_ids,
      amount: data.amount,
      isShowQR: true,
      isDone: false,
      qrCodeImageUrl: data.qr_code_image_url,
      isShowInvoice: true,
    });

    const { open, exit } = PayOSCheckout.usePayOS(this.state.payOSConfig);
    this.state.cancelCallback = exit;
  
    try {
      await open();
    } catch (error) {
      console.error("Error during PayOS checkout:", error);
    }
    this.state.isShowInvoice = true;
  }
  

  async handleShowInvoiceEvent(data) {
    this.state.invoiceLines = data.invoice_ids;
    this.state.amount = data.amount;
    this.state.isShowInvoice = true;
    this.state.isShowQR = false;
  }

  
  onSuccess() {
    this.state.isDone = true;
    setTimeout(() => {
      this.state.isDone = false;
      this.state.isShowQR = false;
      this.state.isShowInvoice = false;
    }, 2000);
  }

  hiddenElementView() {
    const element = this.counterViewRef.el;
      if (element) {
        const actionManagerEl = element.closest(".o_action_manager");
        if (actionManagerEl) {
          const navEl = actionManagerEl.previousElementSibling;
          const mainComponentEl = actionManagerEl.nextElementSibling;
          if (mainComponentEl) {
            mainComponentEl.classList.add("d-none");
          }
          if (navEl) {
            navEl.classList.add("d-none")
          }
          actionManagerEl.classList.remove("o_action_manager");
        }
      }
  }

  async initData() {
    const data = await this.orm.call("z_payos.counter.settings", "get_init_data", [[]], {});
    if (data) {
      this.state.imgBannerList = data.banner_ids ?? this.imgBannerList;
      this.state.payOSConfig.RETURN_URL = data.return_url;
      this.state.channel = `notification.counter_${data.user_id}`
    }
    this.busService.addChannel(this.state.channel);
    this.busService.addEventListener("notification", this.onMessage.bind(this));
  }


  removeQRIframeElement() {
    const list = this.qrIframeRef.el;
    if(list && list.firstElementChild){
      list.removeChild(list.firstElementChild);
    }
  }

  handleCancelQREvent() {
    if (this.state.cancelCallback) {
      this.state.cancelCallback();
    }
    this.state.isShowQR = false;
    this.state.isShowInvoice = false;
  }
}

QRCounter.template = "z_payos.CounterView";
QRCounter.components = { Carousel }
registry.category("actions").add("zen8.action_counter_view", QRCounter);
