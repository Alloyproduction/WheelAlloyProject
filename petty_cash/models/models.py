# -*- coding: utf-8 -*-
from odoo import fields, models, api
import datetime


# class Partner(models.Model):
#     _name = "account.partner"
#     _inherit = ['account.bank.statement', 'mail.thread', 'mail.activity.mixin']


class userjournal(models.Model):
    _inherit = 'res.users'

    journal_id = fields.Many2one('account.journal', string="Jornal Cash")


class account_journal1(models.Model):
    _inherit = ['account.journal', 'account.bank.statement', 'mail.thread', 'mail.activity.mixin']

    @api.multi
    def create_cash_statement(self):
        curruser = self.env.uid
        jorn_id = curruser.journal_id
        ctx = self._context.copy()
        ctx.update({'journal_id': self.id, 'default_journal_id': self.id, 'default_journal_type': 'cash'})
        return {
            'name': _('Create cash statement'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement',
            'context': ctx,
        }



    # customer_of_division_id = fields.Many2one(compute='_get_division_id', comodel_name='purchase.order',
    #                                           string='Customer of the division', store=True)
    #
    # @api.depends('purchase_id')
    # def _get_division_id(self):
    #     if self.purchase_id:
    #         return self.purchase_id.customer_of_division_id.id
    #     else:
    #         return None
    #         # self.customer_of_division_id = self.purchase_id.customer_of_division_id.id
    #     # elif self.partner_id:
    #     #     self.customer_of_division_id = self.partner_id.customer_of_division_id.id
    #
    # @api.multi
    # def action_draft(self):
    #     # self.state = 'stat_draft'
    #     self.ldate = datetime.now()
    #     return self.write({'state': 'stat_draft'})
    #
    #
    #
    # @api.multi
    # def action_confirm(self):
    #     # self.state = 'stat_confirmed'
    #     self.ldate = datetime.now()
    #     return self.write({'state': 'stat_confirmed'})
    #
    #
    # @api.multi
    # def action_process(self):
    #     # self.state = 'stat_process'
    #     self.ldate = datetime.now()
    #     return self.write({'state': 'stat_process'})
    #
    #
