from odoo import fields, models

# _CLAIMSTATES = [
#     ('stat_draft', 'Draft'),
#     ('stat_confirmed', 'Confirmed'),
#     ('stat_process', 'process'),
#     ('stat_won', 'won'),
#     ('stat_lost', 'lost'),
# ]

class Partner(models.Model):
    _name = "account.partner"
    _inherit = ['account.bank.statement', 'mail.thread', 'mail.activity.mixin']


    po_number = fields.Char('Next Action')
    # state = fields.Selection(selection=_CLAIMSTATES,
    #                          string='Status',
    #                          track_visibility='onchange',
    #                          required=True,
    #                          copy=False,
    #                          default='stat_draft')


# @api.multi
# def action_draft(self):
#     # self.state = 'stat_draft'
#     return self.write({'state': 'stat_draft'})
#     self.ldate = datetime.now()
#
#
# # @api.multi
# # def action_confirm(self):
# #     # self.state = 'stat_confirmed'
# #     return self.write({'state': 'stat_confirmed'})
# #     self.ldate = datetime.now()
#
#
# @api.multi
# def action_process(self):
#     # self.state = 'stat_process'
#     return self.write({'state': 'stat_process'})
#     self.ldate = datetime.now()


class journal_post_button(models.Model):
        _inherit = 'account.move'

