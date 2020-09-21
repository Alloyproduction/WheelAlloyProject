# -*- coding: utf-8 -*-
from odoo import http

# class PaymentWorkflow(http.Controller):
#     @http.route('/payment_workflow/payment_workflow/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_workflow/payment_workflow/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_workflow.listing', {
#             'root': '/payment_workflow/payment_workflow',
#             'objects': http.request.env['payment_workflow.payment_workflow'].search([]),
#         })

#     @http.route('/payment_workflow/payment_workflow/objects/<model("payment_workflow.payment_workflow"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_workflow.object', {
#             'object': obj
#         })