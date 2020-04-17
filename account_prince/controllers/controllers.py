# -*- coding: utf-8 -*-
from odoo import http

# class AccountPrince(http.Controller):
#     @http.route('/account_prince/account_prince/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_prince/account_prince/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_prince.listing', {
#             'root': '/account_prince/account_prince',
#             'objects': http.request.env['account_prince.account_prince'].search([]),
#         })

#     @http.route('/account_prince/account_prince/objects/<model("account_prince.account_prince"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_prince.object', {
#             'object': obj
#         })