/** @odoo-module **/

import { Sort } from "./sort/sort";
import { NestedFilter } from "./filter/nested_filter";
import { Notify, NotifyError, NotifyWarning } from "./notify/notify";
import { Paging } from "./paging/paging";
import { ConfirmDialog } from "./confirm_dialog/confirm_dialog";
import { SearchInput } from "./search_input/search_input";
import { Filter } from "./filter/filter";
import { Button } from "./button/button";
import { Icon } from "./icon/icon";
import { Breadcrumb } from "./breadcrumb/breadcrumb";
import { CustomDatePicker } from "./datepicker/custom_datepicker";
import { ScrollLoading } from "./scroll_loading";
import { Carousel } from "./carousel/carousel";
export class SharedComponent {
  static appendComponents(arrayComponents) {
    return {
      Sort,
      NestedFilter,
      Notify,
      NotifyError,
      NotifyWarning,
      Paging,
      ConfirmDialog,
      SearchInput,
      Filter,
      Button,
      Icon,
      Breadcrumb,
      CustomDatePicker,
      ScrollLoading,
      Carousel,
      ...arrayComponents,
    };
  }
}
