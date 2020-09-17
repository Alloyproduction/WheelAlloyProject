
from odoo import api, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move','mail.thread', 'mail.activity.mixin']

    @api.multi
    def total_debit_credit(self):
        res = {}
        for move in self:
            dr_total = 0.0
            cr_total = 0.0
            for line in move.line_ids:
                dr_total += line.debit
                cr_total += line.credit
            res.update({'dr_total': dr_total, 'cr_total': cr_total})
        return res

    @api.multi
    def action_print(self):
        return self.env.ref('journal_entries_print.journal_entries_moce_print_id').report_action(self)


class AccountMove(models.Model):
    _name = "account.payment"
    _inherit = ['account.payment', 'mail.thread', 'mail.activity.mixin']

    @api.multi
    def total_debit_credit(self):
        res = {}
        for move in self:
            dr_total = 0.0
            cr_total = 0.0
            for line in move.move_line_ids:
                dr_total += line.debit
                cr_total += line.credit
            res.update({'dr_total': dr_total, 'cr_total': cr_total})
        return res

    @api.multi
    def action_print2(self):
        return self.env.ref('journal_entries_print.journal_entries_moce_print_id2').report_action(self)
