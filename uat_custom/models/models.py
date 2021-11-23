# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Uatcustom(models.Model):
    _inherit = 'hr.contract'

    wage = fields.Monetary('Basic Salary', digits=(16, 2), required=True,
                           track_visibility="onchange", help="Employee's monthly gross wage.")
    new_total = fields.Monetary(string="Total Salary",  required=False, compute='get_total_custom',
                                readonly=True, store=True)
    conv_allowance = fields.Monetary(string="Conveyance Allowance", help="Conveyance Allowance",
                                     compute='get_conv_hra')
    hra = fields.Monetary(string='Housing Allowance', tracking=True,
                          help="House rent allowance.", compute='get_conv_hra')

    @api.onchange('wage', 'hra', 'travel_allowance', 'conv_allowance')
    def get_total_custom(self):
        for t in self:
            # print(t.new_total)
            t.new_total = t.wage + t.hra + t.conv_allowance + t.travel_allowance
            # print('new_total', t.new_total)

    @api.onchange('wage')
    def get_conv_hra(self):
        for h in self:
            # print(h.hra)
            h.hra = h.wage * 0.25
            h.conv_allowance = h.wage * 0.10
            # print('wwee', h.hra )
