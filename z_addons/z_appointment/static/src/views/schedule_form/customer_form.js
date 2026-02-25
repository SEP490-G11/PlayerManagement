/** @odoo-module **/

const { Component, useState, useRef, markup, onWillStart, onMounted } = owl;
import { CustomDatePicker } from "@z_web/shared/datepicker/custom_datepicker";
import { useAutofocusModal } from "@z_web/hook/useAutoFocus";
import { genderOptions, contactOptions, approachChannelOptions } from "@z_web/constants";
import utils from "@z_web/utils";
import validators from "@z_appointment/validators";
import { ApiService } from "@z_web/services/api_service";
import { customerUrls, groupCustomerUrls } from "../../config";
import { ScrollLoading } from "@z_web/shared/scroll_loading";

export class CustomerForm extends Component {
  setup() {
    let maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 90);

    const customer = {
      name: "",
      gender: "male",
      date: "",
      mobile: "",
      job: "",
      group_id: "",
      contact_source: "",
      approach_channel: "",
      code: "",
      street: ""
    };
    const error = {
      name: "",
      gender: "",
      date: "",
      group_id: "",
    };
    this.state = useState({
      isEdit: false,
      open: false,
      groups: [],
      pageSize: 20,
      customers: [],
      searchText: "",
      customer,
      contacts : contactOptions,
      approach_channels: approachChannelOptions,
      genders: genderOptions,
      defaultForm: { ...customer },
      defaultError: { ...error },
      error,
      isLoading: false,
    });
    this.nameInput = useRef("name-input");
    useAutofocusModal("name-input");
    onWillStart(async () => {
      ApiService.call(groupCustomerUrls.crud, {}, "get").then((res) => {
        this.state.groups = res;
      });
    });
    onMounted(() => {
      this.scrollLoadingRef = utils.getChildComponent(this, "ScrollLoading");
    });
  }
  onSearchCustomer = utils.debounce(() => this.searchCustomer());
  async searchCustomer() {
    this.getCustomer(true);
  }
  async getCustomer(isReset = false) {
    if (isReset) {
      this.scrollLoadingRef.reset();
    }
    const { searchText, pageSize } = this.state;
    const { page } = this.scrollLoadingRef.state;
    const params = {
      input: searchText,
      page_number: page,
      page_size: pageSize,
    };
    if (isReset) {
      this.state.customers = [];
    }
    this.isLoading = true;
    ApiService.call(customerUrls.crud, params, "get")
      .then((res) => {
        this.scrollLoadingRef.setTotalPage(res.total_pages);
        this.state.customers.push(
          ...res.items.map((x) => {
            x.displayText = this.getSearchResultText(x);
            return x;
          })
        );
      })
      .catch((err) => {
        this.state.customers = [];
      })
      .finally(() => {
        this.isLoading = false;
      });
  }
  initForm(id = null) {
    if (!id) {
      this.setCustomer();
      return;
    }
    ApiService.call(customerUrls.crud + id, {}, "get").then((res) => {
      this.setCustomer(res);
    });
  }
  setCustomer(customer = null) {
    this.state.open = false;
    this.state.searchText = "";
    this.state.error = { ...this.state.defaultError };
    this.state.customers = [];
    if (customer) {
      this.state.customer = {
        ...customer,
        group_id: customer.group_id[0] || "",
        contact_source: customer.contact_source || "",
        approach_channel: customer.approach_channel || "",
      };
    } else {
      this.state.customer = {
        ...this.state.defaultForm,
        group_id: this.state.groups[0]?.id || "",
        contact_source: this.state.contacts[0]?.value || "",
        approach_channel: this.state.approach_channels[0]?.value || "",
      };
    }
  }
  onUpdateDate(date) {
    this.state.customer.date = date;
    this.state.error.date = null;
  }
  validCustomerInfo() {
    const { isValid, error } = validators.validatePerson(this.state.customer);
    this.state.error = error;
    return isValid;
  }
  getPlaceholder(placeholder, isHavePlaceHolder) {
    if (isHavePlaceHolder) {
      return placeholder;
    }
    return "";
  }
  getSearchResultText(customer) {
    const result = `${customer.name} - ${customer.mobile}`;
    if (!this.state.searchText || !this.state.searchText.trim()) return result;
    const phoneRegex = /(\+84\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2})|(\d{10})/g;
    const newResult = result.replace(
      phoneRegex,
      function (match) {
        if (match === this.state.searchText) {
          return '<strong class="highlight">' + match + "</strong>";
        }
        return match;
      }.bind(this)
    );
    return markup(newResult);
  }
  onFocus() {
    this.state.open = true;
    this.searchCustomer();
  }
  onBlur() {
    setTimeout(() => {
      this.state.open = false;
    }, 300);
  }
}

CustomerForm.components = { CustomDatePicker, ScrollLoading };
CustomerForm.defaultProps = {};
CustomerForm.template = "z_appointment.CustomerForm";
