import time
import datetime
from dateutil.relativedelta import relativedelta

import odoo
from odoo import SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    journal_id = fields.Many2one('account.journal')
    label = fields.Char()
    debit_account_id = fields.Many2one('account.account')
    credit_account_id = fields.Many2one('account.account')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    journal_id = fields.Many2one('account.journal',
                                 default=lambda self: self.env.user.company_id.journal_id)
    label = fields.Char(default=lambda self: self.env.user.company_id.label)
    debit_account_id = fields.Many2one('account.account',
                                       default=lambda self: self.env.user.company_id.debit_account_id)
    credit_account_id = fields.Many2one('account.account',
                                        default=lambda self: self.env.user.company_id.credit_account_id)

    @api.model
    def create(self, values):
        if 'company_id' in values or 'journal_id' in values \
            or 'label' in values or 'debit_account_id' in values \
                or 'credit_account_id' in values:
            self.env.user.company_id.write({
                    'journal_id': values['journal_id'],
                    'label': values['label'],
                    'debit_account_id': values['debit_account_id'],
                    'credit_account_id': values['credit_account_id']
                 })
        res = super(ResConfigSettings, self).create(values)
        res.company_id.write({
                    'journal_id': values['journal_id'],
                    'label': values['label'],
                    'debit_account_id': values['debit_account_id'],
                    'credit_account_id': values['credit_account_id']
                 })
        return res
