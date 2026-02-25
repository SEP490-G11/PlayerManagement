import json
import logging
import requests
import urllib.parse
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_zns.helpers.constants import BASE_URL
from odoo.addons.z_web.helpers.constants import READABLE_DATE_FORMAT
import datetime

_logger = logging.getLogger(__name__)


class ZMISAUtils:
    @staticmethod
    def _get_misa_url(env=None):
        """Get MISA configuration from system parameters"""
        if env:
            base_url = env['ir.config_parameter'].sudo().get_param(
                'z_invoice.misa_api_url', 
                'https://testapi.meinvoice.vn/api/integration'
            )
        else:
            # Fallback to default values if no environment provided
            base_url = 'https://testapi.meinvoice.vn/api/integration'
            
        return base_url

    @staticmethod
    def call_token_api(appid, taxcode, username, password, env):
        try:
            base_url = ZMISAUtils._get_misa_url(env)
            url = f"{base_url}/auth/token"

            payload = {
                "appid": appid,
                "taxcode": taxcode,
                "username": username,
                "password": password,
            }
            headers = {"Content-Type": "application/json"}
            _logger.info(f"Calling MISA API: {url}")
            _logger.debug(f"Payload: {json.dumps(payload, ensure_ascii=False)}")

            response = requests.post(
                url, headers=headers, json=payload, timeout=30
            )
            _logger.info(f"MISA API Response Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                _logger.info("MISA API call successful")
                return {
                    "success": True,
                    "data": result,
                    "status_code": response.status_code,
                }
            else:
                error_msg = f"MISA API error: {response.status_code} - {response.text}"
                _logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                }

        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            _logger.error(error_msg)
            return {"success": False, "error": error_msg, "status_code": None}
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error - unable to reach MISA API"
            _logger.error(error_msg)
            return {"success": False, "error": error_msg, "status_code": None}
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            _logger.error(error_msg)
            return {"success": False, "error": error_msg, "status_code": None}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {str(e)}"
            _logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "status_code": response.status_code if "response" in locals() else None,
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            _logger.error(error_msg)
            return {"success": False, "error": error_msg, "status_code": None}

    @staticmethod
    def call_invoice_templates_api(
        access_token, year=2024, invoice_with_code=True, ticket=False, env=None
    ):
        try:
            base_url = ZMISAUtils._get_misa_url(env)
            url = f"{base_url}/invoice/templates"

            # Query parameters
            params = {
                "invoiceWithCode": str(invoice_with_code).lower(),
                "ticket": str(ticket).lower(),
                "year": str(year),
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(
                    url, headers=headers, params=params, timeout=30
            )

            _logger.info(
                f"MISA Invoice Templates API Response Status: {response.status_code}"
            )

            if response.status_code == 200:
                result = response.json()
                _logger.info("MISA Invoice Templates API call successful")
                return {
                    "success": True,
                    "data": result,
                    "status_code": response.status_code,
                }
            else:
                error_msg = f"MISA Invoice Templates API error: {response.status_code} - {response.text}"
                _logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                }
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            _logger.error(error_msg)
            return {"success": False, "error": error_msg, "status_code": None}

    @staticmethod
    def call_invoice_unpublish_api(access_token, invoice_data, env=None):
        return ZMISAUtils.api_call("invoice/unpublishview", "POST", access_token, invoice_data, env)
        
    @staticmethod
    def format_error_response(error_message, status_code=None):
        return {
            "success": False,
            "error": error_message,
            "status_code": status_code,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    @staticmethod
    def reget_token(place_id):
        return ZMISAUtils.call_token_api(
            place_id.appid, place_id.tax_id, place_id.email_company, place_id.password, env=place_id.env
        )

    @staticmethod
    def call_invoice_publish_api(access_token, invoice_data, env=None):
        return ZMISAUtils.api_call(
            "invoice", "POST", access_token, invoice_data, env
        )

    @staticmethod
    def call_preview_published_invoice_api(access_token, invoice_data, env=None):
        return ZMISAUtils.api_call(
            "invoice/publishview", "POST", access_token, invoice_data, env
        )
        
    @staticmethod
    def call_cancel_invoice_unpublish_api(access_token, invoice_data, env=None):
        return ZMISAUtils.api_call("invoice/cancel", "POST", access_token, invoice_data, env)
    
    @staticmethod
    def call_send_email_api(access_token, invoice_data, env=None):
        return ZMISAUtils.api_call("invoice/sendemail", "POST", access_token, invoice_data, env)

    @staticmethod
    def api_call(url, method, access_token, data, env=None):
        try:
            base_url = ZMISAUtils._get_misa_url(env)
            url = f"{base_url}/{url}"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            print("data", data)
            response = requests.request(
                method, url, headers=headers, json=data, timeout=30
            )
            print("response", response.json())
            _logger.info(
                f"MISA Invoice Publish API Response Status: {response.status_code}"
            )

            return response.json()

        except Exception as e:
            _logger.error(f"Error calling {url}: {str(e)}")
            return {"success": False, "error": str(e), "status_code": None}
