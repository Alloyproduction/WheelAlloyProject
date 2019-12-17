# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    alloy_digital_signature = fields.Binary(widget="signature")