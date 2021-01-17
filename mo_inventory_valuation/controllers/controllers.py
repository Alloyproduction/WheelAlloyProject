# -*- coding: utf-8 -*-
from odoo import http

# class MoStockReport(http.Controller):
#     @http.route('/mo_stock_report/mo_stock_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mo_stock_report/mo_stock_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mo_stock_report.listing', {
#             'root': '/mo_stock_report/mo_stock_report',
#             'objects': http.request.env['mo_stock_report.mo_stock_report'].search([]),
#         })

#     @http.route('/mo_stock_report/mo_stock_report/objects/<model("mo_stock_report.mo_stock_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mo_stock_report.object', {
#             'object': obj
#         })