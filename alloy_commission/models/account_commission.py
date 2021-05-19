# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountCommissionLine(models.Model):
    _name = 'account.commission.line'
    _inherit = ['mail.thread']

    account_commission_id = fields.Many2one('account.commission')
    product_id = fields.Many2one('product.product')
    description = fields.Char()
    analytic_account_id = fields.Many2one('account.analytic.account')
    analytic_tags_ids = fields.Many2many('account.analytic.tag')
    repair_cost = fields.Float()
    rims_quantity = fields.Float(default=1)
    commission_rate = fields.Float()
    commission_amount = fields.Float(compute='compute_commission_amount', store=True)

    @api.depends('commission_rate', 'rims_quantity')
    def compute_commission_amount(self):
        for record in self:
            record.commission_amount = record.rims_quantity * record.commission_rate

    @api.onchange('product_id')
    def onchange_product_id(self):
        for record in self:
            record.description = record.product_id.name_get()[0][1] if record.product_id.name_get() else ''
            # record.repair_cost = record.product_id.standard_price


class AccountCommission(models.Model):
    _name = 'account.commission'
    _inherit = ['mail.thread']

    name = fields.Char(string='serial number')
    date = fields.Date(default=fields.date.today())
    advisor_id = fields.Many2one('res.partner')
    customer_id = fields.Many2one('res.partner')
    so_number = fields.Char()
    invoice_number = fields.Char()
    invoice_id = fields.Many2one('account.invoice', string='invoice number')
    journal_id = fields.Many2one('account.move')
    account_commission_ids = fields.One2many('account.commission.line', 'account_commission_id', copy=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('completed', 'Completed'),
                                        ('paid', 'paid'),
                                        ], default='draft')

    @api.multi
    def action_create_journal(self):
        for record in self:
            account_move_obj = self.env['account.move']
            account_move_line_obj = self.with_context(dict(self._context, check_move_validity=False)).env['account.move.line']
            account_obj = account_move_obj.create({
                'journal_id': record.env.user.company_id.journal_id.id,
                'date': record.date,
                'ref': record.invoice_number,
            })
            for line in record.account_commission_ids:
                account_move_line_obj.sudo().create({
                    'move_id': account_obj.id,
                    'account_id': self.env.user.company_id.credit_account_id.id,
                    'analytic_account_id': line.analytic_account_id.id,
                    'analytic_tag_ids': [(6, 0, line.analytic_tags_ids.ids)],
                    'partner_id': record.advisor_id.id,
                    'name': self.env.user.company_id.label,
                    'debit': 0.0,
                    'credit': line.commission_amount,
                })
                account_move_line_obj.sudo().create({
                    'move_id': account_obj.id,
                    'account_id': self.env.user.company_id.debit_account_id.id,
                    'analytic_account_id': line.analytic_account_id.id,
                    'analytic_tag_ids': [(6, 0, line.analytic_tags_ids.ids)],
                    'partner_id': record.advisor_id.id,
                    'name': self.env.user.company_id.label,
                    'debit': line.commission_amount,
                    'credit': 0.0,
                })
            self.sudo().write({'journal_id': account_obj.id, 'state': 'completed'})
            account_obj.sudo().action_post()

    @api.multi
    def action_reconcile(self):
        self.sudo().write({'state': 'paid'})

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('account.commission')
        res = super(AccountCommission, self).create(values)
        return res
