/** @odoo-module **/
import { ListRenderer } from "@web/views/list/list_renderer";
import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";
import { onMounted, onPatched } from "@odoo/owl";
import { ApiService } from "@z_web/services/api_service";
import { groupCustomerUrls, placeUrls } from "@z_appointment/config";

var places = []
var groupDatas = []
patch(ListRenderer.prototype, {
    setup() {
        super.setup(...arguments);

        if (this.props.list && this.props.list.resModel !== "z_glass_order"
          && this.props.list.resModel !== "z_appointment.appointment"
          && this.props.list.resModel !== "account.move"
          && this.props.list.resModel !== "res.partner"
          && this.props.list.resModel !== "account.payment"
          && this.props.list.resModel !== "helpdesk.ticket"
        ) {
            return;
        }
        if (this.props.list && this.props.list.context?.disable_advance_list_search) {
            return;
        }
        browser.sessionStorage.setItem('domainlist', JSON.stringify([])); // Replaced localStorage with sessionStorage

        onMounted(async () => {
            await Promise.all([
              this.getListPlace(),
              this.getListGroupCustomer()
            ]);
            this._renderSearchPanel();
        });

        onPatched(() => {
            this._renderSearchPanel();
        });
    },

    async getListPlace() {
        const res = await ApiService.call(placeUrls.crud, {}, "get");
        places = JSON.parse(JSON.stringify(res));
    },

     async getListGroupCustomer() {
        const res = await ApiService.call(groupCustomerUrls.crud, {}, "get");
        groupDatas = JSON.parse(JSON.stringify(res));
    },

    _renderSearchPanel() {
        const List = this.props.list;
        const rootRef = this.rootRef.el;
        const tableRef = this.tableRef.el;

        const hasBlockSearchClass = rootRef.parentElement.parentElement.classList.contains('block_advance_search');
        if (hasBlockSearchClass){
            return 
        }
        
        tableRef.removeAttribute('style');
        const columns = this.allColumns.filter((col) => {
            if ((col.optional && this.optionalActiveFields[col.name] === false) ||  col.invisible == 'True' || col.column_invisible == "1" ||  col.column_invisible == "True") {
                return false;
            }
            return true;
        });

        const $tr1 = $('<tr>').append(columns.map(this._renderHeaderCellSearch.bind(this)));

        if (this.hasSelectors) {
            $tr1.prepend($('<td>').addClass('o_list_record_selector'));
        }

        if (this.isStudioEditable || this.displayOptionalFields) {
            $tr1.append($('<td>').addClass('o_list_record_selector'));
        }

        if ($(tableRef).find('.search_td').length) {
            $(tableRef).find('.search_td').parent().replaceWith($tr1);
        } else {
            $tr1.insertAfter($(tableRef).find('tr')[0]);
        }

        rootRef.querySelectorAll('thead tr td.search_td input').forEach((a) => a.addEventListener('keyup', this._onfilter.bind(this)));
        rootRef.querySelectorAll('thead tr td.search_td select').forEach((a) => a.addEventListener('change', this._onSearch.bind(this)));
        rootRef.querySelectorAll('.search_button').forEach((a) => a.addEventListener('click', this._onSearch.bind(this)));
        rootRef.querySelectorAll('.remove_button').forEach((a) => a.addEventListener('click', this._onRemove.bind(this)));
        rootRef.querySelectorAll('thead tr td').forEach((a) => a.addEventListener('keypress', this._onKeyPress.bind(this)));
    },

    _renderHeaderCellSearch(node) {
        const List = this.props.list;
        const search_tr = $($('tr')[1]).find('input.input_text');
        const old_domain = JSON.parse(browser.sessionStorage.getItem('domainlist'));
        const input_dict = {};
        const self = this;
        const $td = $('<td>', {
            class: 'search_td',
        });

        for (let i = 0; i < search_tr.length; i++) {
            const field = $(search_tr[i]).attr('name');
            const value = $(search_tr[i]).val();
            input_dict[String(field)] = value;
        }

        if (node.type !== 'field') {
            return $td;
        }
        const {
        name = '',
        string = '',
        widget = ''
    } = node || {};
        const searched_value = old_domain.filter(function (domain) {
            return domain[0] === name;
        });
        var widget_list = ["float_time", "remaining_days", "res_partner_many2one",
            "many2many_tags", "monetary", "date", "many2one_avatar_user", "badge",
            "task_with_hours", "timesheet_uom", "sol_product_many2one", 
            "visit_state_selection", "state_selection"];
        var value_of_tr = searched_value.length > 0 ? searched_value[0][2] : ""
        var field = List.fields[name];

        if (name) {
            $td.attr('data-name', name);
        } else if (string) {
            $td.attr('data-string', string);
        }
        if (!field) {
            return $td;
        }

        const description = string || field.string;

        // search elements
       var search_div = $('<div>').attr({
            'class': 'search_div d-inline-flex auto-overflow'
        });
        var $input = $('<input>').attr({
            name: name,
            data_name: name,
            data_text: string,
            // placeholder: 'description',
            autocomplete: "autocomplete",
            'class': 'input_text min-wp-50'
        });
        var search_button = $('<button>').attr({
            type: 'button',
            name: name,
            'class': 'search_button fa fa-search'
        });
        var remove_button = $('<button>').attr({
            type: 'button',
            name: name,
            'class': 'remove_button fa fa-remove',
        });
        // Prepare search bars
        if (!widget || widget_list.includes(widget)) {
            if (string !== " " && field.store) {
                if (field.type == 'selection'
                  || (name == 'place_id' && places.length)
                  || (name == 'is_paid')
                  || (name == 'customer_group_id' && groupDatas.length)
                ) {
                    if (name == 'place_id') {
                        let selections = []
                        places.forEach(item => {
                            selections.push([item.name, item.name])
                        })
                        field.selection = JSON.parse(JSON.stringify(selections))
                    }

                    if (name == 'is_paid') {
                        let selections = []
                        selections.push([ 'false' , "Chưa thanh toán"])
                        selections.push([ 'true' , "Đã thanh toán"])
                        field.selection = JSON.parse(JSON.stringify(selections))
                    }

                    if (name == 'customer_group_id') {
                        let selections = []
                        groupDatas.forEach(item => {
                            selections.push([item.name, item.name])
                        })
                        field.selection = JSON.parse(JSON.stringify(selections))
                    }

                    const selection_input = '<select class="input_text input_select" type="select" name=' + name + ' data_name=' + name + ' data_text=' + string  + ' style="height:25px;">'
                    var option = '<option selected="selected" class="text-muted" value></option>';
                    $.each(field.selection, function (index, value) {
                        option += '<option value="' + value[0] + '">' + value[1] + '</option>'
                        $(selection_input).add('<option value="' + value[0] + '">' + value[1] + '</option>')
                    });
                    if (typeof value_of_tr == 'boolean') {
                        value_of_tr = value_of_tr.toString()
                    }
                    if (value_of_tr) {
                        if (typeof value_of_tr == 'string') {
                            value_of_tr = [value_of_tr];
                        }
                        value_of_tr.forEach((val) => {
                            var $value_tag = $('<span>').attr({
                                title: val,
                                name: val,
                                value: val,
                                class: 'd-inline-flex badge',
                            })
                            var tag_val = "";
                            field.selection.forEach((value) => {
                                if (val == value[0]) {
                                    tag_val = value[1];
                                }
                            });
                            $value_tag.append($(
                                `<div class="o_tag_badge_text">${tag_val}</div>`
                            ))
                            $value_tag.val(val);
                            $value_tag.css('background-color', '#dfdfdf');
                            $value_tag.css('border-radius', '20px');
                            $value_tag.css('font-size', '15px');
                            search_div.append($value_tag)
                        })
                    }

                    var sel_in = selection_input + option + '</select>'
                    search_div.find('span').append(remove_button);
                    search_div.append(sel_in)
                    search_div.append(search_button)
                    $td.append(search_div)
                }
                if (['integer', 'float', 'monetary'].includes(field.type)) {
                    $input.attr({ type: 'number' });

                    $input.text(description)
                    if (value_of_tr) {
                        if (typeof value_of_tr == 'number') {
                            value_of_tr = [value_of_tr];
                        }
                        if (value_of_tr === true) {
                            value_of_tr = ['true'];
                        }
                        value_of_tr.forEach((val) => {
                            var $value_tag = $('<span>').attr({
                                title: val,
                                name: val,
                                value: val,
                                class: 'd-inline-flex badge',
                            })
                            $value_tag.append($(
                                `<div class="o_tag_badge_text">${val}</div>`
                            ))
                            $value_tag.val(val);
                            $value_tag.css('background-color', '#dfdfdf');
                            $value_tag.css('border-radius', '20px');
                            $value_tag.css('font-size', '15px');
                            search_div.append($value_tag)
                        })
                    }
                    search_div.find('span').append(remove_button);
                    search_div.append($input);
                    search_div.append(search_button);
                    $td.append(search_div);
                }
                if (['many2one', 'char', 'many2many', 'boolean'].includes(field.type)
                  && name != 'place_id' && name != 'is_paid' && name != 'customer_group_id'
                ) {
                    $input.attr({ type: 'text' });

                    $input.text(description)
                    const values_of_tr = searched_value.map((val) => {
                        return val[2];
                    })
                    if (values_of_tr.length) {
                        values_of_tr.forEach((val) => {
                            var $value_tag = $('<span>').attr({
                                title: val,
                                name: val,
                                value: val,
                                class: 'd-inline-flex badge',
                            })
                            $value_tag.append($(
                                `<div class="o_tag_badge_text">${val}</div>`
                            ))
                            $value_tag.val(val);
                            $value_tag.append(remove_button);
                            $value_tag.css('background-color', '#dfdfdf');
                            $value_tag.css('border-radius', '20px');
                            $value_tag.css('font-size', '15px');
                            search_div.append($value_tag)
                        })
                    }
                    search_div.find('span').append(remove_button);
                    search_div.append($input);
                    search_div.append(search_button);
                    $td.append(search_div);
                }
                if (field.type == 'datetime' || field.type == 'date') {
                    if (searched_value.length > 1 && searched_value[0][2]) {
                        searched_value[0][2] = searched_value[0][2].toString()
                    }
                    if (searched_value.length > 1 && searched_value[1][2]) {
                        searched_value[1][2] = searched_value[1][2].toString()
                    }
                    var hasDateTime = searched_value.length > 1 && self.checkDateTime(searched_value[0][2]) == "datetime" ? true : false
                    var value_of_tr1 = searched_value.length > 1 ? hasDateTime ? (self._convertDateTimeRange(searched_value[0][2])) + '-' 
                        + self._convertDateTimeRange(searched_value[1][2]) : (self._convertDateRange(searched_value[0][2])) + '-' 
                        + self._convertDateRange(searched_value[1][2]) : ""
                    var search_div = $('<div>').attr({
                        'class': 'search_div'
                    });
                    var $input_date1 = $('<input>').attr({
                        type: 'text',
                        name: name,
                        placeholder: 'Khoảng ngày',
                        autocomplete: "autocomplete",
                        width: '150px',
                        'class': 'input_text',
                        'style': 'min-width:180px !important'
                    });
                    var search_button = $('<button>').attr({
                        type: 'button',
                        name: name,
                        'class': 'search_button  fa fa-search'
                    });
                    var remove_button = $('<button>').attr({
                        type: 'button',
                        name: name,
                        'class': 'remove_button  fa fa-remove hidden_button',
                    });
                    if ($input_date1) {
                        $input_date1.daterangepicker({
                            autoUpdateInput: false,
                            locale: {
                                cancelLabel: 'Clear'
                            }
                        });
                        $input_date1.on('apply.daterangepicker', function (ev, picker) {
                            $input_date1.val(picker.startDate.format('DD/MM/YYYY') + '-' + picker.endDate.format('DD/MM/YYYY'));
                            var e = $.Event("keypress", {
                                which: 13
                            });
                            $input_date1.trigger(e);
                            e.keyCode = 13  
                            self._onfilter(e)
                            $input_date1.change()
                        });

                        $input_date1.on('cancel.daterangepicker', function (ev, picker) {
                            $input_date1.val('');
                            var e = $.Event("keypress", {
                                which: 13
                            });
                            $input_date1.trigger(e);
                            e.keyCode = 13
                            self._onfilter(e)
                            $input_date1.change()
                        });
                        $input_date1.text(description)
                        $input_date1.val(value_of_tr1)

                        if (value_of_tr1) {
                            $(search_button).addClass('hidden_button');
                            $(remove_button).removeClass('hidden_button');
                        }
                        if ($(search_button).hasClass('hidden_button')) {
                            $input_date1.attr('readonly', 'readonly');
                            $input_date1.css('background-color', '#dfdfdf');
                            $input_date1.css('border-radius', '20px');
                        }
                        search_div.append($input_date1)
                        search_div.append(remove_button)
                        search_div.append(search_button)
                        $td.append(search_div)
                    }
                }
            }
        }
        return $td;
    },
    _onKeyPress: function (ev) {
        ev.stopPropagation(); // to prevent jquery's blockUI to cancel event
    },

    _onSearch: function (event) {
        var self = this
        var field_name = $(event.currentTarget).attr('name')
        let all_input_tags = $($('tr')[1]).find('input.input_text,select.input_text')
        if (!all_input_tags.length) {
            all_input_tags = $($('tr')[5]).find('input.input_text,select.input_text')
        }
        all_input_tags.filter(function (el) {
            if (all_input_tags[el].name == field_name) {
                var e = $.Event("keypress", {
                    which: 13
                });
                $(all_input_tags[el]).trigger(e);
                e.keyCode = 13
                self._onfilter(e)
            }
        });
    },

     _onRemove: function (event) {
        const List = this.props.list;
        var self = this;
        var updated_domain = [];
        var old_domain = JSON.parse(browser.sessionStorage.getItem('domainlist'));
        var field_name = $(event.currentTarget).attr('name');
        var tag_value = $(event.currentTarget.parentElement).attr('value');
        let all_input_tags = $($('tr')[1]).find('input.input_text');

        if (!all_input_tags.length) {
            all_input_tags = $($('tr')[5]).find('input.input_text')
        }
        const ListDomain = old_domain;
        if (["monetary", "float", "integer", "selection"].includes(List.fields[field_name].type)
          || field_name == 'is_paid') {
            ListDomain.map(function (el) {
                tag_value = !isNaN(tag_value) ? parseFloat(tag_value) : tag_value;
                tag_value = tag_value.toString()
                if (field_name == 'is_paid') {
                    el[2] = [el[2].toString()]
                }
                if (field_name == el[0] && el[2].includes(tag_value)) {
                    const index = el[2].indexOf(tag_value);
                    index > -1 ? el[2].splice(index, 1) : false;
                    el[2].length ? updated_domain.push(el) : false;
                }
                else {
                    updated_domain.push(el)
                }
            });
        }
        else if (["date", "datetime"].includes(List.fields[field_name].type)) {
            ListDomain.map(function (el) {
                if (field_name != el[0]) {
                    updated_domain.push(el)
                }
            });
        }
        else {
            ListDomain.map(function (el) {
                if (field_name != el[0] || tag_value != el[2]) {
                    updated_domain.push(el)
                }
                if (el == '|') {
                    let index = updated_domain.indexOf('|');
                    updated_domain.splice(index, 1);
                }
            });
        }
        browser.sessionStorage.setItem('domainlist', JSON.stringify(updated_domain));
        var indexes = []
        var to_update = []
        var count = 0
        updated_domain.forEach(el => {
            if (indexes.length && el[1] == 'ilike' && updated_domain[indexes[indexes.length - 1]][0] == el[0]) {
                to_update.push(indexes[indexes.length - 1])
            } else if (el[1] == 'ilike') {
                indexes.push(count)
            }
            count += 1;
        })
        to_update.reverse()
        to_update.forEach(A => {
            updated_domain.splice(A, 0, '|');
        })
        self.perform_search(self, updated_domain);
        self._renderSearchPanel();
    },

    _onfilter: function (e) {
        const List = this.props.list;
        const old_domain = JSON.parse(browser.sessionStorage.getItem('domainlist'));

        if (e.key === 'Enter' || e.keyCode === 13) {
            var domain_list = [];
            var self = this
            let all_input_tags = $($('tr')[1]).find('input.input_text')
            if (!all_input_tags.length) {
                all_input_tags = $($('tr')[5]).find('input.input_text')
            }

            let all_select_tags = $($('tr')[1]).find('select.input_text')
            if (!all_select_tags.length) {
                all_select_tags = $($('tr')[5]).find('select.input_text')
            }

            var search_tr = all_input_tags.filter(function (el) {
                return all_input_tags[el].value
            });
            if (search_tr.length == 0) {
                self.perform_search(self, domain_list);
            }
            for (var i = 0; i < search_tr.length; i++) {
                var field = $(search_tr[i]).attr('name')
                var string = search_tr[i].textContent
                var value = $(search_tr[i]).val()
                if (value) {
                    if (List.fields[field].type == "date") {
                        const array = value.split('-')
                        var startDate = moment(array[0].trim(), "DD/MM/YYYY").format("DD/MM/YYYY");
                        var endDate = moment(array[1].trim(), "DD/MM/YYYY").format("DD/MM/YYYY");
                        if (startDate == 'Invalid date' || endDate == 'Invalid date') {
                            window.alert("Please enter valid input for " + string);
                        } else {
                            domain_list.push([field, '>=', self._convertToOdooFormat(startDate)])
                            domain_list.push([field, '<=', self._convertToOdooFormat(endDate)])
                        }
                    } else if (List.fields[field].type == "datetime") {
                        var startDate = moment(value.split('-')[0].trim(), "DD/MM/YYYY").format("MM/DD/YYYY HH:mm:ss");
                        var endDate = moment(value.split('-')[1].trim(), "DD/MM/YYYY").format("MM/DD/YYYY 23:59:59");
                        if (startDate == 'Invalid date' || endDate == 'Invalid date') {
                            window.alert("Please enter valid input for " + string);
                        } else {
                            domain_list.push([field, '>=', startDate])
                            domain_list.push([field, '<=', endDate])
                        }

                    } else if (["monetary", "float", "integer"].includes(List.fields[field].type)) {
                        var domain = old_domain.filter((domain) => {
                            return domain[0] == field;
                        })
                        if (domain.length) {
                            if (!domain[0][2].includes(parseFloat(value))) {
                                domain[0][2].push(parseFloat(value));
                            }
                            domain_list.push(domain[0])
                        }
                        else {
                            domain_list.push([field, 'in', [parseFloat(value)]]);
                        }
                    } else {
                        if (old_domain.length) {
                            old_domain.forEach((domain) => {
                                if (domain[0] == field) {
                                    domain_list.push(domain);
                                }
                            })
                            if(!old_domain.map((d)=>{return d[2]}).includes(value)){
                                domain_list.push([field, 'ilike', value]);
                            }
                        }
                        else {
                            domain_list.push([field, 'ilike', value]);
                        }
                    }
                }
            }
            $(all_select_tags).each(function (index, elem) {
                var elem_value = $(elem).val();
                var elem_field = $(elem).attr('data_name');
                if (elem_value.length > 0) {
                    if (List.fields[elem_field].type == 'selection') {
                        var domain = old_domain.filter((domain) => {
                            return domain[0] == elem_field
                        })
                        if (domain.length) {
                            if (!domain[0][2].includes(elem_value)) {
                                domain[0][2].push(elem_value);
                            }
                            domain_list.push(domain[0])
                        }
                        else {
                            domain_list.push([elem_field, 'in', [elem_value]])
                        }
                    }
                    else {
                        if (elem_value === 'false') {
                          domain_list.push([elem_field, '=', false])
                        } else if (elem_value === 'true') {
                           domain_list.push([elem_field, '=', true])
                        } else {
                            domain_list.push([elem_field, '=', elem_value])
                        }
                    }
                }
            });

            old_domain.forEach((domain) => {
                var avail = domain_list.filter(a => {
                    if (domain[1] == 'in' && typeof a[2] != "boolean") {
                        return domain[2].every(f => a[2].includes(f)) && a[0] == domain[0]
                    }
                    else {
                        return a[2].toString() == domain[2].toString() && a[0] == domain[0]
                    }
                }).length
                if (!(avail) && self.checkDateTime(domain[2]) == "Invalid") {
                    domain_list.push(domain)
                }
            })
            browser.sessionStorage.setItem('domainlist', JSON.stringify(domain_list));
            var indexes = []
            var to_update = []
            var count = 0
            domain_list.forEach(el => {
                if (indexes.length && el[1] == 'ilike' && domain_list[indexes[indexes.length - 1]][0] == el[0]) {
                    to_update.push(indexes[indexes.length - 1])
                } else if (el[1] == 'ilike') {
                    indexes.push(count)
                }
                count += 1;
            })
            to_update.reverse()
            to_update.forEach(A => {
                domain_list.splice(A, 0, '|');
            })
            self.perform_search(self, domain_list);
        }
    },

    _convertToOdooFormat: function (dateStr) {
        // Kiểm tra định dạng đầu vào
        const regex = /^(\d{2})\/(\d{2})\/(\d{4})$/;
        const match = dateStr.match(regex);
    
        if (match) {
            // Tách ngày, tháng, năm từ chuỗi
            const day = match[1];
            const month = match[2];
            const year = match[3];
    
            // Chuyển đổi thành định dạng YYYY-MM-DD
            return `${year}-${month}-${day}`;
        } else {
            throw new Error("Định dạng ngày tháng không hợp lệ. Vui lòng sử dụng định dạng DD/MM/YYYY.");
        }
    },
    checkDateTime: function (value) {
        if (moment(value, "MM/DD/YYYY HH:mm:ss", true).isValid()) {
            return "datetime";
        } else if (moment(value, "YYYY-MM-DD", true).isValid()) {
            return "date";
        } else {
            return "Invalid";
        }
    },
    _convertDateRange: function (dateRange) {
        const [startYear, startMonth, startDay] = dateRange.split('-');
        // Kết hợp các ngày vào chuỗi kết quả theo định dạng DD/MM/YYYY
        return `${startDay}/${startMonth}/${startYear}`;
    },
    _convertDateTimeRange: function (dateRange) {
        const [datePart, timePart] = dateRange.split(" ");
        const [month, day, year] = datePart.split("/");
        return `${day}/${month}/${year} ${timePart}`;
    },
    perform_search: async function (self, domain_list) {
        const searchModel = self.env.searchModel;
        const list = self.props.list;

        if (self.isX2Many && domain_list.length) {
            const readIds = await self.env.model.orm.read(
                self.props.nestedKeyOptionalFieldsData.model,
                [list.model.__bm_load_params__.res_id],
                [list.__fieldName__])

            domain_list.push(['id', 'in', readIds[0][list.__fieldName__]])

            var resIds = await self.env.model.orm.search(list.resModel, domain_list, {
                limit: session.active_ids_limit,
                context: list.context,
            });
            await list.load({ 'ids': resIds })
            list.model.notify()
        }
        else {
            searchModel.ak_domains = domain_list;
            searchModel._notify();
        }
    },
});
