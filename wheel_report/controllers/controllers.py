# -*- coding: utf-8 -*-
from odoo import http

# class WheelReport(http.Controller):
#     @http.route('/wheel_report/wheel_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wheel_report/wheel_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wheel_report.listing', {
#             'root': '/wheel_report/wheel_report',
#             'objects': http.request.env['wheel_report.wheel_report'].search([]),
#         })

#     @http.route('/wheel_report/wheel_report/objects/<model("wheel_report.wheel_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wheel_report.object', {
#             'object': obj
#         })