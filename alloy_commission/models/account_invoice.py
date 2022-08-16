# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrAppraisal(models.Model):
    _inherit = 'account.invoice'

    commission_count = fields.Float(compute='compute_commission_count')
    x_studio_service_provider = fields.Many2one('res.partner')
    active = fields.Boolean('Active',default=lambda *a: 1)

    def compute_commission_count(self):
        account_commission = self.env['account.commission'].search_count([('invoice_id', '=', self.id)])
        if account_commission:
            self.commission_count = account_commission
        else:
            self.commission_count = 0.0

    def action_open_commission_account(self):
        commission_obj = self.env['account.commission']
        commission_obj_id = commission_obj.sudo().search([('invoice_id', '=', self.id)], limit=1)
        if commission_obj_id:
            return {
                'name': 'Commissions',
                'res_model': 'account.commission',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_id': commission_obj_id.id,
                'domain': [('invoice_id', '=', self.id)],
                'context': {'default_invoice_id': self.id,
                            'default_customer_id': self.partner_id.id,
                            'default_advisor_id': self.x_studio_service_provider.id,
                            'default_invoice_number': self.number,
                            'default_so_number': self.origin,
                            }
            }
        else:
            repair_cost = 0.0
            repair_cost = sum([line.price_unit for line in self.invoice_line_ids])
            product_id = self.env['product.product']
            p = product_id.sudo().search([('name', '=', 'Commission Product')])
            if p:
                product = p
            else:
                product = product_id.sudo().create({'name':'Commission Product'})
            commission_id = commission_obj.sudo().create({
                'invoice_id': self.id,
                'customer_id': self.partner_id.id,
                'advisor_id': self.x_studio_service_provider.id,
                'invoice_number': self.number,
                'so_number': self.origin,
                'account_commission_ids': [(0, 0, {
                    'product_id': product.id,
                    'description': product.name_get()[0][1] if product.name_get() else '',
                    'analytic_tags_ids': [(6, 0, line[0].analytic_tag_ids.ids) for line in self.invoice_line_ids if line.analytic_tag_ids],
                    'repair_cost': repair_cost,
                    'rims_quantity': len(self.invoice_line_ids),
                    'commission_rate': 1,
                })]
            })
            return {
                'name': 'Commissions',
                'res_model': 'account.commission',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_id': commission_id.id,
                'domain': [('invoice_id', '=', self.id)],
                'context': {'default_invoice_id': self.id,
                            'default_customer_id': self.partner_id.id,
                            'default_advisor_id': self.x_studio_service_provider.id,
                            'default_invoice_number': self.number,
                            'default_so_number': self.origin,
                            }
                }
