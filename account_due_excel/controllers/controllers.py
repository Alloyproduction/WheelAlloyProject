# -*- coding: utf-8 -*-
from odoo import http

# class AccountDueExcel(http.Controller):
#     @http.route('/account_due_excel/account_due_excel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_due_excel/account_due_excel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_due_excel.listing', {
#             'root': '/account_due_excel/account_due_excel',
#             'objects': http.request.env['account_due_excel.account_due_excel'].search([]),
#         })

#     @http.route('/account_due_excel/account_due_excel/objects/<model("account_due_excel.account_due_excel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_due_excel.object', {
#             'object': obj
#         })