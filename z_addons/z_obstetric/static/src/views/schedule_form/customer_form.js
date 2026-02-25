/** @odoo-module */
import {patch} from "@web/core/utils/patch";
import {CustomerForm} from "@z_appointment/views/schedule_form/customer_form";
import validators from "../../validators/appointment";
import {obstetricsContactOptions} from "../../constants/index";
const { useEffect } = owl;

patch(CustomerForm.prototype, {
    setup() {
        super.setup();
        const customer = {
            name: "",
            gender: "female",
            date: "",
            mobile: "",
            job: "",
            group_id: "",
            code: "",
            street: "",
        };
        const error = {
            name: "",
            gender: "",
            date: "",
            group_id: "",
            street: "",
        };
        this.state.defaultForm = {
            ...customer
        };
        this.state.customer = {...customer}
        this.state.defaultError = {
            ...error
        };
        this.state.contacts = obstetricsContactOptions;
        this.state.error = {...error}
        useEffect(
            ()=>{
              if( this.state.customer.group_id == "" && this.state.groups.length > 0){
                this.state.customer.group_id =  this.state.groups[0]?.id ?? ""
              }
            },
            ()=>[
                this.state.customer.group_id
            ]
          )
    },

    setCustomer(customer = null) {
        super.setCustomer();
        if (customer) {
            this.state.customer = {
                ...customer,
                group_id: customer.group_id[0] || "",
            };
        } else {
            this.state.customer = {
                ...this.state.defaultForm,
                group_id: ""
            };
        }
    },

    validCustomerInfo() {
        const {isValid, error} = validators.validatePerson(this.state.customer);
        this.state.error = error;
        return isValid;
    }
});
