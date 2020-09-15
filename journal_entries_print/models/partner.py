from odoo import fields, models


class Partner(models.Model):
    _name = "account.partner"
    _inherit = ['account.bank.statement', 'mail.thread', 'mail.activity.mixin']


class journal_post_button(models.Model):
    _inherit = 'account.move'
