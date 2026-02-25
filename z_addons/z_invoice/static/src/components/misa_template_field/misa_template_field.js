/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component, useState, onWillStart } from "@odoo/owl";

export class MisaTemplateField extends Component {
    setup() {
        super.setup();
        this.state = useState({
            templates: [],
            loading: false,
            error: null,
            selectedTemplate: null
        });
        console.log("this.props", this.props);
        this.rpc = useService("rpc");
        
        onWillStart(async () => {
            await this.loadTemplates();
        });
    }
    
    async loadTemplates() {
        this.state.loading = true;
        this.state.error = null;
        
        try {
            // Call the backend method to fetch templates
            const result = await this.rpc("/web/dataset/call_kw", {
                model: "z_invoice.publish_vat_invoice",
                method: "get_misa_templates",
                args: [],
                kwargs: {}
            });
            
            if (result.success) {
                this.state.templates = result.data || [];
                // Set initial value if props.value exists
                if (this.props.value) {
                    this.state.selectedTemplate = this.props.value;
                }
            } else {
                this.state.error = result.error || "Failed to load templates";
            }
        } catch (error) {
            console.error("Error loading templates:", error);
            this.state.error = "Network error occurred";
        } finally {
            this.state.loading = false;
        }
    }
    
    onTemplateChange(ev) {
        const templateId = ev.target.value;
        this.state.selectedTemplate = templateId;
        // Call backend to update the field immediately
        console.log("this.props", this.props);
        
            
            // Trigger change event
            if (this.props.record && this.props.record.setDirty) {
                this.props.record.setDirty();
            }

    }
    
    get selectedTemplateName() {
        if (!this.state.selectedTemplate) return "";
        const template = this.state.templates.find(t => t.IPTemplateID === this.state.selectedTemplate);
        return template ? template.TemplateName : "";
    }
}

MisaTemplateField.template = "z_invoice.MisaTemplateField";
MisaTemplateField.props = {
    ...standardFieldProps,
    value: { type: String, optional: true },
};

export const misaTemplateField = {
  component: MisaTemplateField,
  supportedTypes: ["char"],
};

registry.category("fields").add("misa_template", misaTemplateField);
