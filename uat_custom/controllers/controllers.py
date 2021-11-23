# -*- coding: utf-8 -*-
from odoo import http

# class UatCustom(http.Controller):
#     @http.route('/uat_custom/uat_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/uat_custom/uat_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('uat_custom.listing', {
#             'root': '/uat_custom/uat_custom',
#             'objects': http.request.env['uat_custom.uat_custom'].search([]),
#         })

#     @http.route('/uat_custom/uat_custom/objects/<model("uat_custom.uat_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('uat_custom.object', {
#             'object': obj
#         })