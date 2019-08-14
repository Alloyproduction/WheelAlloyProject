# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_

class ResPartneralloy(models.Model):
    _inherit = 'res.partner'

    companyloc= fields.Many2one('alloy.location',string="Company Location")

class alloylocation(models.Model):
    _name = 'alloy.location'
    name = fields.Char(string="Comp Location")
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100