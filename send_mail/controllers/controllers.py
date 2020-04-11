# -*- coding: utf-8 -*-
from odoo import http

# class SendMail(http.Controller):
#     @http.route('/send_mail/send_mail/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/send_mail/send_mail/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('send_mail.listing', {
#             'root': '/send_mail/send_mail',
#             'objects': http.request.env['send_mail.send_mail'].search([]),
#         })

#     @http.route('/send_mail/send_mail/objects/<model("send_mail.send_mail"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('send_mail.object', {
#             'object': obj
#         })