# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _init_data_resource_calendar(self):
        self.search([('resource_calendar_id', '=', False)])._create_resource_calendar()
