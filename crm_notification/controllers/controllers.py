# -*- coding: utf-8 -*-
from odoo import http

# class CrmNotification(http.Controller):
#     @http.route('/crm_notification/crm_notification/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_notification/crm_notification/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_notification.listing', {
#             'root': '/crm_notification/crm_notification',
#             'objects': http.request.env['crm_notification.crm_notification'].search([]),
#         })

#     @http.route('/crm_notification/crm_notification/objects/<model("crm_notification.crm_notification"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_notification.object', {
#             'object': obj
#         })