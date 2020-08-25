# -*- coding: utf-8 -*-
from odoo import http

# class InvoiceCustomFilter(http.Controller):
#     @http.route('/invoice_custom_filter/invoice_custom_filter/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_custom_filter/invoice_custom_filter/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_custom_filter.listing', {
#             'root': '/invoice_custom_filter/invoice_custom_filter',
#             'objects': http.request.env['invoice_custom_filter.invoice_custom_filter'].search([]),
#         })

#     @http.route('/invoice_custom_filter/invoice_custom_filter/objects/<model("invoice_custom_filter.invoice_custom_filter"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_custom_filter.object', {
#             'object': obj
#         })