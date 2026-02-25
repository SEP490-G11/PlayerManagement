/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { FileInput } from "@web/core/file_input/file_input";
import { useX2ManyCrud } from "@web/views/fields/relational_utils";
import { Component, useState } from "@odoo/owl";

const accepted_image_file_extensions = [
    "jpg",
    "jpeg",
    "png",
]

const accepted_other_file_extensions = [
    "pdf",
]

export class Many2ManyBinaryFieldPreview extends Component {
    static template = "z_web.Many2ManyBinaryFieldPreview";
    static components = {
        FileInput,
    };
    static props = {
        ...standardFieldProps,
        acceptedFileExtensions: { type: String, optional: true },
        className: { type: String, optional: true },
        numberOfFiles: { type: Number, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.operations = useX2ManyCrud(() => this.props.record.data[this.props.name], true);
        this.state = useState({
            previewUrl: "",
            isShowPreview: false,
            extType: "",
        })
    }

    get uploadText() {
        return this.props.record.fields[this.props.name].string;
    }
    get files() {
        return this.props.record.data[this.props.name].records.map((record) => {
            return {
                ...record.data,
                id: record.resId,
            };
        });
    }

    openPreview(url, ext){


        if( accepted_image_file_extensions.includes(ext) || accepted_other_file_extensions.includes(ext) ){
        this.state.extType = ext;
        this.state.previewUrl = url;
        this.state.isShowPreview = true;
        }
        else{
            this.notification.add(_t("Không hỗ trợ mở file"), {
                title: _t("Lỗi hiển thị"),
                type: "danger",
            });
        }
    }

    closePreview(){
        this.state.previewUrl = "";
        this.state.isShowPreview = false;
    }

    getUrl(id) {
        return "/web/content/" + id ;
    }

    getExtension(file) {
        return file.name.replace(/^.*\./, "");
    }

    async onFileUploaded(files) {
        const accepted_file_extensions = [...accepted_image_file_extensions,...accepted_other_file_extensions]
        for (const file of files) {
            if (file.error) {
                return this.notification.add(file.error, {
                    title: _t("Uploading error"),
                    type: "danger",
                });
            }
            
            if (!accepted_file_extensions.includes(file.filename.replace(/^.*\./, ""))){
                return this.notification.add(_t("Không hỗ trợ định dạng file"), {                    
                    title: _t("Lỗi tải lên"),
                    type: "danger",
                });
            }
            await this.operations.saveRecord([file.id]);
        }
    }

    get isImage(){
        return accepted_image_file_extensions.includes(this.state.extType);
    }

    async onFileRemove(deleteId) {
        const record = this.props.record.data[this.props.name].records.find(
            (record) => record.resId === deleteId
        );
        this.operations.removeRecord(record);
    }
}

export const many2ManyBinaryFieldPreview = {
    component: Many2ManyBinaryFieldPreview,
    supportedOptions: [
        {
            label: _t("Accepted file extensions"),
            name: "accepted_file_extensions",
            type: "string",
        },
        {
            label: _t("Number of files"),
            name: "number_of_files",
            type: "integer",
        },
    ],
    supportedTypes: ["many2many"],
    isEmpty: () => false,
    relatedFields: [
        { name: "name", type: "char" },
        { name: "mimetype", type: "char" },
    ],
    extractProps: ({ attrs, options }) => ({
        acceptedFileExtensions: options.accepted_file_extensions,
        className: attrs.class,
        numberOfFiles: options.number_of_files,
    }),
};

registry.category("fields").add("many2many_binary_preview", many2ManyBinaryFieldPreview);