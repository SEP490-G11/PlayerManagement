

/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { CharField, charField } from "@web/views/fields/char/char_field";
import { useService } from "@web/core/utils/hooks";

export class CustomerDetailFieldBs extends CharField {

  setup() {
    this.customer = this.props.record.data[this.props.name] ?? null;
    this.action = useService("action");
    this.orm = useService("orm");
    console.log("---->", this.customer);
    }

  get genderAndAgeText(){
    const space = this.customer.gender && this.customer.age ? " - " : "";
    return `(${this.customer.gender}${space}${this.customer.age == false ? "" : this.customer.age  })`;
  }

  async openAction(id){
    const action = await this.orm.call("res.partner", "open_customer_form", [[id]], {});
    this.action.doAction(action);
  }

  get partnerUrl() {
    const id = this.customer?.id;
    return id ? `/web#id=${id}&model=res.partner&view_type=form` : "#";
}

onClick(ev, id) {
    // Nếu là Ctrl+Click, Cmd+Click (Mac), hoặc Middle click → KHÔNG chặn
    if (ev.ctrlKey || ev.metaKey || ev.button === 1) {
        return;
    }

    // Click trái bình thường → mở qua doAction
    ev.preventDefault();
    ev.stopPropagation();
    this.openAction(id);
}

}
CustomerDetailFieldBs.template = "z_web.CustomerDetailFieldBs";

export const customerDetailFieldBs = {
  ...charField,
  component: CustomerDetailFieldBs,
};

registry.category("fields").add("customer_detail_field_bs", customerDetailFieldBs);
