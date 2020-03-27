# -*- coding: utf-8 -*-
from odoo import http

# class DisableCreate(http.Controller):
#     @http.route('/disable_create/disable_create/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/disable_create/disable_create/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('disable_create.listing', {
#             'root': '/disable_create/disable_create',
#             'objects': http.request.env['disable_create.disable_create'].search([]),
#         })

#     @http.route('/disable_create/disable_create/objects/<model("disable_create.disable_create"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('disable_create.object', {
#             'object': obj
#         })