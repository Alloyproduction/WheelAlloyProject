# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class WebsiteConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    app_stop_subscribe = fields.Boolean('Stop Odoo Subscribe(Performance Improve)', help=u"Check to stop Odoo Subscribe function")

    @api.model
    def get_values(self):
        res = super(WebsiteConfig, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        app_stop_subscribe = True if ir_config.sudo().get_param('app_stop_subscribe') == "True" else False

        res.update(
            app_stop_subscribe=app_stop_subscribe,
        )
        return res

    def set_values(self):
        res = super(WebsiteConfig, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("app_stop_subscribe", self.app_stop_subscribe or "False")
        return res
