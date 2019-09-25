# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrderSource(models.Model):
    _name = "sale.order.source"
    name = fields.Char()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_studio_source_2 = fields.Many2one("sale.order.source", 'Source')
    is_individual = fields.Boolean(compute="_compute_is_individual", store=True)

    @api.depends('partner_id')
    def _compute_is_individual(self):
        for rec in self:
            if rec.partner_id.company_type == 'company':
                rec.is_individual = True
