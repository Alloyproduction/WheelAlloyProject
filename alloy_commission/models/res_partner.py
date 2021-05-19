# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    advisor_id = fields.Many2one('res.partner', string='service advisor')
