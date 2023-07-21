# -*- coding: utf-8 -*-
# from odoo import http


# class DisableCalendarResourse(http.Controller):
#     @http.route('/disable_calendar_resourse/disable_calendar_resourse', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/disable_calendar_resourse/disable_calendar_resourse/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('disable_calendar_resourse.listing', {
#             'root': '/disable_calendar_resourse/disable_calendar_resourse',
#             'objects': http.request.env['disable_calendar_resourse.disable_calendar_resourse'].search([]),
#         })

#     @http.route('/disable_calendar_resourse/disable_calendar_resourse/objects/<model("disable_calendar_resourse.disable_calendar_resourse"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('disable_calendar_resourse.object', {
#             'object': obj
#         })
