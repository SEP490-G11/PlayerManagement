from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request 
import werkzeug


class ZCounterController(http.Controller):        
    @http.route(
        ["/web/counters",],
        type="http")
    def generate_test_result_urls(self, **kw):
        action = request.env['ir.actions.client'].sudo().search([('tag', '=','zen8.action_counter_view' )])
        if not action:
            return {'error': 'Action not found'} 
        url = f"/web#action={action.id}"
        print(url)
        return werkzeug.utils.redirect(url)
