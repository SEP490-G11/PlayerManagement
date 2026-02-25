/** @odoo-module **/
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";
import utils from "../utils";

export class ApiService {
  constructor() {
    this.orm = useService("orm");
  }

  handleApi(model, api, params = [], options = {}) {
    return new Promise((resolve, reject) => {
      this.orm
        .call(model, api, params, options)
        .then((result) => {
          if (result.success) {
            resolve(result.data);
            if (result.message) {
              utils.showToast(result);
            }
          } else {
            const error = {
              code: result.code,
              message: result.message,
              isShowToast: false,
            };
            reject(error);
          }
        })
        .catch(() => {
          reject({
            code: 500,
            message: "Đã có lỗi xảy ra. Vui lòng thử lại sau.",
            isShowToast: true,
          });
        });
    });
  }

  callApi(model, api, params = [], options = {}) {
    return new Promise((resolve, reject) => {
      this.handleApi(model, api, params, options)
        .then((result) => {
          resolve(result);
        })
        .catch((error) => {
          if (error.isShowToast) {
            utils.showToast(error);
          }
          reject(error);
        });
    });
  }
  static call(url, payload = {}, method = "get", blobResponseType = false) {
    return new Promise((resolve, reject) => {
      ApiService.apiCallData(url, payload, method, blobResponseType)
        .then((res) => {
          resolve(res.data);
          if (res.message) {
            utils.showToast({ ...res, success: true });
          }
        })
        .catch((error) => {
          const _error = {
            success: false,
            code: error.code || 500,
            message: error.message || "Đã có lỗi xảy ra. Vui lòng thử lại sau.",
            detail: error.detail,
            isShowToast: "isShowToast" in error ? error.isShowToast : true,
          };
          if (_error.isShowToast) {
            utils.showToast(_error);
          }
          reject(_error);
        });
    });
  }

  static prefixMapValues({ prefix, endpoints }) {
    const result = {};
    for (const key in endpoints) {
      const value = endpoints[key];
      result[key] = [prefix, value].join("/");
      if (result[key][result[key].length - 1] !== "/") {
        result[key] += "/";
      }
    }
    return result;
  }
  static fileInObject(data) {
    return !!Object.values(data).filter((item) => {
      if (item instanceof Array) {
        return !!item.filter((x) => x instanceof Blob).length;
      }
      return item instanceof Blob;
    }).length;
  }
  static getJsonPayload(data) {
    const formData = new FormData();
    formData.append("data", JSON.stringify(data));
    formData.append("csrf_token", odoo.csrf_token);
    return {
      data: formData,
      "Content-Type": "application/json",
    };
  }

  static getFormDataPayload(data) {
    const formData = new FormData();
    for (const key in data) {
      const value = data[key];
      if (Array.isArray(value) && value.every((item) => item instanceof Blob)) {
        for (const file of value) {
          formData.append(`${key}[]`, file, file.name);
        }
      } else if (value instanceof Blob) {
        formData.append(key, value, value.name);
      } else {
        formData.append(key, value);
      }
    }
    return {
      data: formData,
      "Content-Type": "",
    };
  }

  static apiCallData(url, params = {}, method = "get", blobResponseType = false) {
    const { data, "Content-Type": contentType } = ApiService.fileInObject(params)
      ? ApiService.getFormDataPayload(params)
      : ApiService.getJsonPayload(params);
    const config = {
      method,
      url,
      responseType: blobResponseType ? "blob" : "json",
    };
    if (["get"].includes(method.toLowerCase())) {
      const query = new URLSearchParams(params).toString();
      config.url = [config.url, query].join("?");
    } else {
      config.data = data;
    }
    return new Promise((resolve, reject) => {
      browser
        .fetch(config.url, {
          body: config.data,
          method: config.method,
        })
        .then((res) => {
          res[config.responseType]()
            .then((x) => {
              if (!res.ok) {
                reject(x);
              }
              resolve(x);
            })
            .catch((err) => {
              reject({});
            });
        });
    });
  }
  static checkResponseStatus(response) {
    if (response.status === 502) {
      throw new Error("Failed to fetch");
    }
  }
}
