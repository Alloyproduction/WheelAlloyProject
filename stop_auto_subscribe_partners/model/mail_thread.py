# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from distutils.util import strtobool 


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.multi
    def check_Partner_in_users(self,partner_ids):
        b=False
        all_users = self.env['res.users'].search([])
        all_partner_ids =[]
        for u in all_users:
            all_partner_ids.append(u.partner_id.id)
        print(" id of partners " , partner_ids)
        print(" id of partners ", all_partner_ids)
        if  partner_ids in all_partner_ids:
            b=True
        return b

    @api.multi
    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        ir_config = self.env['ir.config_parameter']
        app_stop_subscribe = bool(strtobool(ir_config.sudo().get_param('app_stop_subscribe')))

        if app_stop_subscribe and (not self.check_Partner_in_users(partner_ids)) :
            return
        else:
            return super(MailThread, self).message_subscribe(partner_ids, channel_ids, subtype_ids)

    @api.multi
    def _message_auto_subscribe(self, updated_values):
        ir_config = self.env['ir.config_parameter']
        app_stop_subscribe = bool(strtobool(ir_config.sudo().get_param('app_stop_subscribe')))
        if app_stop_subscribe :
            return
        else:
            return super(MailThread, self)._message_auto_subscribe(updated_values)

    @api.multi
    def _message_auto_subscribe_notify(self, partner_ids, template):
        ir_config = self.env['ir.config_parameter']
        app_stop_subscribe = bool(strtobool(ir_config.sudo().get_param('app_stop_subscribe')))
        if app_stop_subscribe and (not self.check_Partner_in_users(partner_ids)):
            return
        else:
            return super(MailThread, self)._message_auto_subscribe_notify(partner_ids, template)