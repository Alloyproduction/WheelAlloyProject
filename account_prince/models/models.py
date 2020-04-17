# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_
from odoo.exceptions import UserError, ValidationError


class account_payment2(models.Model):

    _inherit = "account.payment"

    # _inherit = ['mail.thread', 'account.abstract.payment']
    def get_recipients(self):
        group = self.env['res.groups'].search(
            [('name', 'in', ['Accountant', '', 'Advisor', 'Billing'])])  # self.env.ref('stock.group_stock_manager')
        print(group)
        recipients = []
        for g in group:
            for recipient in g.users:
                if recipient.partner_id.id not in recipients:
                    recipients.append(recipient.partner_id.id)
                    print(recipient.name)

        return recipients


    def send_m(self, msubj="", mbody=""  , recipient_partners=[]):

        if msubj != "":
            msgsubject = msubj

        if mbody != "":
            msgbody = mbody

        print(recipient_partners)

        if len(recipient_partners):
            invoide_id = self.env['account.invoice'].browse(self._context.get('active_id', False))
            invoide_id.message_post(body=msgbody,
                              subtype='mail.mt_comment',
                              subject=msgsubject,
                              partner_ids=recipient_partners,
                              message_type='comment')
    @api.multi
    def action_validate_invoice_payment(self):
        res =super(account_payment2, self).action_validate_invoice_payment()
        print(self)
        recipients = self.get_recipients()
        print(recipients)
        for x in recipients:
            print(x)

        recipients =[300, 280]
        self.send_m("Bill Paid","This Bill paid",recipients)
        return   res

# class account_prince(models.Model):
#     _name = 'account_prince.account_prince'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100