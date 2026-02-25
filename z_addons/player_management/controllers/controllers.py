# -*- coding: utf-8 -*-
# from odoo import http


# class PlayerManagement(http.Controller):
#     @http.route('/player_management/player_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/player_management/player_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('player_management.listing', {
#             'root': '/player_management/player_management',
#             'objects': http.request.env['player_management.player_management'].search([]),
#         })

#     @http.route('/player_management/player_management/objects/<model("player_management.player_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('player_management.object', {
#             'object': obj
#         })

