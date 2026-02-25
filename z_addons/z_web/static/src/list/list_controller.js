/** @odoo-module */
import {ListController} from '@web/views/list/list_controller';
import {patch} from 'web.utils';

import {ImportButtonMixin} from './import_button_mixin'

patch(ListController.prototype, 'web_import_button', ImportButtonMixin)
