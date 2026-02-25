/** @odoo-module */

export const ImportButtonMixin = {
  isDisplayImportButton() {
    const config = this.env.config;
    return (
      !!JSON.parse(config.viewArch.getAttribute("import") || "1") &&
      !!JSON.parse(config.viewArch.getAttribute("create") || "1")
    );
  },

  actionImport() {
    const { context, resModel } = this.env.searchModel;
    this.actionService.doAction({
      type: "ir.actions.client",
      tag: "import",
      params: { model: resModel, context },
    });
  },
};
