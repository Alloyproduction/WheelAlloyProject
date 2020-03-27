# -*- coding: utf-8 -*-

from odoo import models, fields, api



class ResUsers(models.Model):
    _inherit = "res.users"

    disable_create_edit = fields.Boolean(string='Disable Create',)

# class disable_create(models.Model):
#     _name = 'disable_create.disable_create'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100