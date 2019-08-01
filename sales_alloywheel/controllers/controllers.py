# -*- coding: utf-8 -*-
from odoo import http

# class SalesAlloywheel(http.Controller):
#     @http.route('/sales_alloywheel/sales_alloywheel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_alloywheel/sales_alloywheel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_alloywheel.listing', {
#             'root': '/sales_alloywheel/sales_alloywheel',
#             'objects': http.request.env['sales_alloywheel.sales_alloywheel'].search([]),
#         })

#     @http.route('/sales_alloywheel/sales_alloywheel/objects/<model("sales_alloywheel.sales_alloywheel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_alloywheel.object', {
#             'object': obj
#         })