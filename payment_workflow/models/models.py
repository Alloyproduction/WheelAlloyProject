# -*- coding: utf-8 -*-

from odoo import models, fields, api


class stock_form(models.Model):
    _inherit = 'purchase.order'

    name = fields.Char()
