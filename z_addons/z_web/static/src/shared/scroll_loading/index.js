/** @odoo-module **/

const { Component, useState, onWillStart, useRef } = owl;

export class ScrollLoading extends Component {
  static props = {
    onLoad: Function,
    height: String,
    slots: {
      type: Object,
      optional: true,
    },
    className: { type: String, optional: true },
  };
  setup() {
    this.boxItemRef = useRef("boxItem");
    this.state = useState({
      page: 1,
      totalPage: 0,
    });
    onWillStart(async () => {});
  }
  reset() {
    this.state = {
      page: 1,
      totalPage: 0,
    };
    if (this.boxItemRef.el) this.boxItemRef.el.scrollTop = 0;
  }

  setTotalPage(page) {
    this.state.totalPage = page;
  }
  handleScroll(e) {
    const { scrollTop, scrollHeight, clientHeight } = e.srcElement;
    if (scrollTop + clientHeight >= scrollHeight - 5 && this.state.page < this.state.totalPage) {
      this.state.page = this.state.page + 1;
      this.props.onLoad();
    }
  }
}

ScrollLoading.template = "z_web.ScrollLoading";
ScrollLoading.components = {};
