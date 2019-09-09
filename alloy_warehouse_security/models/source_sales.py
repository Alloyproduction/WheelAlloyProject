# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderSource(models.Model):
    _name = "sale.order.source"
    name = fields.Char()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_studio_source_2 = fields.Many2one("sale.order.source", 'Source')


class ResUser(models.Model):
    _inherit = "res.users"

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')

    # default=lambda self: self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1))


