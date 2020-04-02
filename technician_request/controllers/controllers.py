# -*- coding: utf-8 -*-
from odoo import http

# class TechnicianRequest(http.Controller):
#     @http.route('/technician_request/technician_request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/technician_request/technician_request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('technician_request.listing', {
#             'root': '/technician_request/technician_request',
#             'objects': http.request.env['technician_request.technician_request'].search([]),
#         })

#     @http.route('/technician_request/technician_request/objects/<model("technician_request.technician_request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('technician_request.object', {
#             'object': obj
#         })