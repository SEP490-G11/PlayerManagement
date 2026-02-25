/** @odoo-module **/

const { Component, onWillUpdateProps } = owl;
import { defaultPageNumber } from "@z_web/constants";
import utils from "../../utils";

export class Paging extends Component {
  static props = {
    fetchData: Function,
    exportData: Function,
    pagingData: Object,
    isShowExport: { type: Boolean, optional: true, default: true },
  };

  static defaultProps = {
    isShowExport: true,
  };

  setup() {
    this.state = this.props.pagingData || {
      pages: [1],
      gotoPage: 1,
      totalPages: 1,
      totalRecords: 0,
      currentPage: 1,
      startRecord: 0,
      endRecord: 0,
    };

    onWillUpdateProps((nextProps) => {
      this.state = nextProps.pagingData;
      this.state.pages = utils.generatePagingList(
        nextProps.pagingData.pages,
        nextProps.pagingData.currentPage,
        nextProps.pagingData.totalPages
      );
    });

    if (this.props.pagingData) {
      this.state.pages = utils.generatePagingList(this.state.pages, this.state.currentPage, this.state.totalPages);
    }
  }

  // Handle jump page by in put
  handlePageChange(event) {
    const page = parseInt(this.state.gotoPage);
    if (event.keyCode == 13) {
      if (page > 0 && page <= this.state.totalPages) {
        this.handlePageClick(page);
      } else {
        this.state.gotoPage = defaultPageNumber;
        this.handlePageClick(this.state.gotoPage);
      }
    }
  }

  // Handle click to page
  async handlePageClick(page) {
    if (page && page <= this.state.totalPages && page > 0) {
      await this.props.fetchData(Number(page), {});
    } else {
      await this.props.fetchData(defaultPageNumber, {});
    }
  }

  // When click to previous button go to previous page
  previousPage() {
    if (this.state.currentPage > 1) {
      this.handlePageClick(this.state.currentPage - 1);
    }
  }

  // When click to next page button go to next page
  nextPage() {
    if (this.state.currentPage < this.state.totalPages) {
      this.handlePageClick(this.state.currentPage + 1);
    }
  }

  // Export data to excel
  async exportData() {
    if (this.props.exportData) {
      this.props.exportData();
    } else {
      utils.showToastUpdatingFunction();
    }
  }

  //Remove current page value when click to input
  onInputClick() {
    this.state.currentPage = "";
  }
}

Paging.template = "z_web.Paging";
