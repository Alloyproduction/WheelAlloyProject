# -*- coding: utf-8 -*-

from odoo import models, api


class QualityCheck(models.Model):
    _inherit = "product.template"

    @api.onchange('seller_ids')
    def _onchange_seller_ids(self):
        for record in self:
            if record.seller_ids:
                for line in record.seller_ids:
                    record.standard_price = line.price
