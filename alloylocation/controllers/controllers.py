# -*- coding: utf-8 -*-
from odoo import http

# class Alloylocation(http.Controller):
#     @http.route('/alloylocation/alloylocation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alloylocation/alloylocation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('alloylocation.listing', {
#             'root': '/alloylocation/alloylocation',
#             'objects': http.request.env['alloylocation.alloylocation'].search([]),
#         })

#     @http.route('/alloylocation/alloylocation/objects/<model("alloylocation.alloylocation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alloylocation.object', {
#             'object': obj
#         })