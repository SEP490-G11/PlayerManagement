/** @odoo-module **/
const { Component, useState, onWillStart, onWillUnmount, onWillUpdateProps } = owl;

export class Carousel extends Component {
  static props = {
    className: String,
    slides: Array,
  };

  setup() {
    this.state = useState({
      slides: this.props.slides,
      currentSlide: 1,
    });

    this.interval = null;

    onWillStart(() => {
      this.startAutoSlide();
    });
    onWillUpdateProps(async (nextProps) => {
      this.state.slides = nextProps.slides;
      this.state.currentSlide
    });

    onWillUnmount(() => {
      this.stopAutoSlide();
    });
  }

  startAutoSlide() {
    this.interval = setInterval(() => {
      this.nextSlide();
    }, 5000);
  }

  stopAutoSlide() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
  }

  nextSlide() {
    const totalSlides = this.state.slides.length;
    this.state.currentSlide = this.state.currentSlide < totalSlides ? this.state.currentSlide + 1 : 1;
  }

  prevSlide() {
    const totalSlides = this.state.slides.length;
    this.state.currentSlide = this.state.currentSlide > 1 ? this.state.currentSlide - 1 : totalSlides;
  }
}

Carousel.template = "z_web.Carousel";
