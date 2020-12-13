# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

import datetime, time




# class Partner(models.Model):
#     _name = "account.partner"
#     _inherit = ['account.bank.statement', 'mail.thread', 'mail.activity.mixin']


class userjournal(models.Model):
    _inherit = 'res.users'

    journal_id = fields.Many2one('account.journal', string="Jornal Cash")


class account_journal1(models.Model):
    _inherit = 'account.bank.statement'
    _rec_name = 'code'

    state = fields.Selection([('open','New'),('stat_prepar', 'Prepare'),
                              ('stat_check', 'Check'),
                              ('stat_audit', 'Audit'),
                              ('stat_review', 'Review'), ('confirm', 'Approve and Validated')],
                             string='Status', required=True, readonly=True, copy=False,
                             default='open')
    # """ READ ME """

    # Start inheriting every thing related to open and confirm status

    name = fields.Char(string='Reference', states={'open': [('readonly', False)]}, copy=False, readonly=True)
    reference = fields.Char(string='External Reference', states={'open': [('readonly', False)]}, copy=False, readonly=True, help="Used to hold the reference of the external mean that created this statement (name of imported file, reference of online synchronization...)")
    accounting_date = fields.Date(string="Accounting Date", help="If set, the accounting entries created during the bank statement reconciliation process will be created at this date.\n"
        "This is useful if the accounting period in which the entries should normally be booked is already closed.",
        states={'open': [('readonly', False)]}, readonly=True)
    date = fields.Date(required=True, states={'confirm': [('readonly', True)]}, index=True, copy=False, default=fields.Date.context_today)


    @api.multi
    def unlink(self):
        for statement in self:
            if statement.state != 'open':
                raise UserError(_('In order to delete a bank statement, you must first cancel it to delete related journal items.'))
            # Explicitly unlink bank statement lines so it will check that the related journal entries have been deleted first
            statement.line_ids.unlink()
        return super(account_journal1, self).unlink()

    @api.multi
    def button_open(self):
        """ Changes statement state to Running."""
        for statement in self:
            if not statement.name:
                context = {'ir_sequence_date': statement.date}
                if statement.journal_id.sequence_id:
                    st_number = statement.journal_id.sequence_id.with_context(**context).next_by_id()
                else:
                    SequenceObj = self.env['ir.sequence']
                    st_number = SequenceObj.with_context(**context).next_by_code('account.bank.statement')
                statement.name = st_number
            statement.state = 'open'

    @api.model
    def _default_opening_balance(self):
        #Search last bank statement and set current opening balance as closing balance of previous one
        journal_id = self._context.get('default_journal_id', False) or self._context.get('journal_id', False)
        if journal_id:
            return self._get_opening_balance(journal_id)
        return 0

    balance_start = fields.Monetary(string='Starting Balance', states={'confirm': [('readonly', True)]}, default=_default_opening_balance)
    balance_end_real = fields.Monetary('Ending Balance', states={'confirm': [('readonly', True)]})


    @api.model
    def _default_journal(self):
        journal_type = self.env.context.get('journal_type', False)
        company_id = self.env['res.company']._company_default_get('account.bank.statement').id
        if journal_type:
            journals = self.env['account.journal'].search([('type', '=', journal_type), ('company_id', '=', company_id)])
            if journals:
                return journals[0]
        return self.env['account.journal']

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'confirm': [('readonly', True)]}, default=_default_journal)

    line_ids = fields.One2many('account.bank.statement.line', 'statement_id', string='Statement lines',
                               states={'confirm': [('readonly', True)]}, copy=True)
    move_line_ids = fields.One2many('account.move.line', 'statement_id', string='Entry lines',
                                    states={'confirm': [('readonly', True)]})



    # overrided function from account.bank.statement view_id is view_bank_statement_form
    # customized 'stat_approve', it was 'open'

    @api.multi
    def button_confirm_bank(self):
        self._balance_check()
        statements = self.filtered(lambda r: r.state == 'stat_review')
        for statement in statements:
            moves = self.env['account.move']
            # `line.journal_entry_ids` gets invalidated from the cache during the loop
            # because new move lines are being created at each iteration.
            # The below dict is to prevent the ORM to permanently refetch `line.journal_entry_ids`
            line_journal_entries = {line: line.journal_entry_ids for line in statement.line_ids}
            for st_line in statement.line_ids:
                # upon bank statement confirmation, look if some lines have the account_id set. It would trigger a journal entry
                # creation towards that account, with the wanted side-effect to skip that line in the bank reconciliation widget.
                journal_entries = line_journal_entries[st_line]
                st_line.fast_counterpart_creation()
                if not st_line.account_id and not journal_entries.ids and not st_line.statement_id.currency_id.is_zero(
                        st_line.amount):
                    raise UserError(
                        _('All the account entries lines must be processed in order to close the statement.'))
            moves = statement.mapped('line_ids.journal_entry_ids.move_id')
            if moves:
                moves.filtered(lambda m: m.state != 'posted').post()
            statement.message_post(body=_('Statement %s confirmed, journal items were created.') % (statement.name,))
        statements.write({'state': 'confirm', 'date_done': time.strftime("%Y-%m-%d %H:%M:%S")})


    # End inheriting
    # End inheriting

    code = fields.Char(string=' Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('account.bank.statement') or _('New')
        result = super(account_journal1, self).create(vals)
        return result

    ###############################
    ###############################
    ###############################
    ###############################

    @api.multi
    def create_cash_statement1(self):
        curruser = self.env.user

        jorn_id = curruser.journal_id
        print(jorn_id)
        ctx = self._context.copy()
        ctx.update({'journal_id': jorn_id.id, 'default_journal_id': jorn_id.id, 'default_journal_type': 'cash'})
        return {
            'name': _('Create cash statement'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.bank.statement',
            'context': ctx,
        }

    @api.multi
    def action_prepar(self):

        msg_body = " Prepar by... " + "" + self.env.user.name
        msg_sub = "Check Petty Cash [" + self.code + "]"

        groups = self.env['res.groups'].search([('name', '=', 'Petty Cash Check')])
        recipient_partners = []
        for group in groups:
            for recipient in group.users:
                if recipient.partner_id.id not in recipient_partners:
                    recipient_partners.append(recipient.partner_id.id)
        if len(recipient_partners):
            self.message_post(body=msg_body,
                              subtype='mt_comment',
                              subject=msg_sub,
                              partner_ids=recipient_partners,
                              message_type='comment')

        return self.write({'state': 'stat_prepar'})

    @api.multi
    def action_check(self):

        msg_body = " Checked by... " + "" + self.env.user.name
        msg_sub = "Audit Petty Cash [" + self.code + "]"

        groups = self.env['res.groups'].search([('name', '=', 'Petty Cash Audit')])
        recipient_partners = []
        for group in groups:
            for recipient in group.users:
                if recipient.partner_id.id not in recipient_partners:
                    recipient_partners.append(recipient.partner_id.id)
        if len(recipient_partners):
            self.message_post(body=msg_body,
                              subtype='mt_comment',
                              subject=msg_sub,
                              partner_ids=recipient_partners,
                              message_type='comment')

        return self.write({'state': 'stat_check'})

    @api.multi
    def action_audit(self):

        msg_body = "Audit by... " + "" + self.env.user.name
        msg_sub = "Review Petty Cash [" + self.code + "]"

        groups = self.env['res.groups'].search([('name', '=', 'Petty Cash Review')])
        recipient_partners = []
        for group in groups:
            for recipient in group.users:
                if recipient.partner_id.id not in recipient_partners:
                    recipient_partners.append(recipient.partner_id.id)
        if len(recipient_partners):
            self.message_post(body=msg_body,
                              subtype='mt_comment',
                              subject=msg_sub,
                              partner_ids=recipient_partners,
                              message_type='comment')

        return self.write({'state': 'stat_audit'})

    @api.multi
    def action_review(self):

        # msg_body = " Review by... " + self.env.user.name
        #
        # msg_sub = "Approve and Validate Petty Cash [" + self.code + "]"
        #
        # groups = self.env['res.groups'].search([('name', '=', 'Petty Cash Validate')])
        # recipient_partners = []
        # for group in groups:
        #     for recipient in group.users:
        #         if recipient.partner_id.id not in recipient_partners:
        #             recipient_partners.append(recipient.partner_id.id)
        # if len(recipient_partners):
        #     self.message_post(body=msg_body,
        #                       subtype='mt_comment',
        #                       subject=msg_sub,
        #                       partner_ids=recipient_partners,
        #                       message_type='comment')

        return self.write({'state': 'stat_review'})

    @api.multi
    def action_validate(self):

        return self.write({'state': 'confirm'})

    @api.multi
    def button_draft(self):

        return self.write({'state': 'open'})


    #
    # def send_mail_msg(self, msgsubject, msgbody, recipient_partners):
    #     self.message_post(body=msgbody,
    #                       subtype='mt_comment',
    #                       subject=msgsubject,
    #                       partner_ids=recipient_partners,
    #                       message_type='comment',
    #                       )
#
#     @api.multi
#     def action_prepar(self):
#         # self.state = 'stat_prepar'
#         return self.write({'state': 'stat_prepar'})
#         # self.ldate = datetime.now()
#
#     groups = self.env['res.groups'].search([('name', '=', 'Petty Cash Check')])
#     recipient_partners = []
#     for group in groups:
#         for recipient in group.users:
#             if recipient.partner_id.id not in recipient_partners:
#                 recipient_partners.append(recipient.partner_id.id)
#
#
#     def send_mail_msg(self,msgsubject,msgbody,recipient_partners):
#         self.message_post(body=msgbody,
#                               subtype='mt_comment',
#                               subject=msgsubject,
#                               partner_ids=recipient_partners,
#                               message_type='comment',
#                              )
#
#    ###################################################################################################
#
#     @api.multi
#     def action_check(self):
#         # self.state = 'stat_check'
#         return self.write({'state': 'stat_check'})
#         # self.ldate = datetime.now()
#
#
#      groups = self.env['res.groups'].search([('name', '=', 'Petty Cash Check')])
#     recipient_partners = []
#     for group in groups:
#         for recipient in group.users:
#             if recipient.partner_id.id not in recipient_partners:
#                 recipient_partners.append(recipient.partner_id.id)
#
#     def send_mail_msg1(self,msgsubject,msgbody,recipient_partners):
#         self.message_post(body=msgbody,
#                               subtype='mt_comment',
#                               subject=msgsubject,
#                               partner_ids=recipient_partners,
#                               message_type='comment',
#                              )
# ####################################################################################################################
#
#     @api.multi
#     def action_review(self):
#         # self.state = 'stat_recheck'
#         return self.write({'state': 'stat_recheck'})
#         # self.ldate = datetime.now()
#
#
#         groups = self.env['res.groups'].search([('name', '=', 'Petty Cash Review')])
#     recipient_partners = []
#     for group in groups:
#         for recipient in group.users:
#             if recipient.partner_id.id not in recipient_partners:
#                 recipient_partners.append(recipient.partner_id.id)
#
#
#     def send_mail_msg2(self,msgsubject,msgbody,recipient_partners):
#         self.message_post(body=msgbody,
#                               subtype='mt_comment',
#                               subject=msgsubject,
#                               partner_ids=recipient_partners,
#                               message_type='comment',
#                              )
# #####################################################################################################
#     @api.multi
#     def action_approve(self):
#         # self.state = 'stat_approve'
#         return self.write({'state': 'stat_approve'})
#
#     groups = self.env['res.groups'].search([('name', '=', 'Petty Cash Approve')])
#     recipient_partners = []
#     for group in groups:
#         for recipient in group.users:
#             if recipient.partner_id.id not in recipient_partners:
#                 recipient_partners.append(recipient.partner_id.id)
#
#
#     def send_mail_msg3(self,msgsubject,msgbody,recipient_partners):
#         self.message_post(body=msgbody,
#                               subtype='mt_comment',
#                               subject=msgsubject,
#                               partner_ids=recipient_partners,
#                               message_type='comment',
#                              )
# ################################################################################################################
#
# @api.multi
# def button_confirm_bank(self):
#     self._balance_check()
#     statements = self.filtered(lambda r: r.state == 'open')
#     for statement in statements:
#         moves = self.env['account.move']
#         # `line.journal_entry_ids` gets invalidated from the cache during the loop
#         # because new move lines are being created at each iteration.
#         # The below dict is to prevent the ORM to permanently refetch `line.journal_entry_ids`
#         line_journal_entries = {line: line.journal_entry_ids for line in statement.line_ids}
#         for st_line in statement.line_ids:
#             #upon bank statement confirmation, look if some lines have the account_id set. It would trigger a journal entry
#             #creation towards that account, with the wanted side-effect to skip that line in the bank reconciliation widget.
#             journal_entries = line_journal_entries[st_line]
#             st_line.fast_counterpart_creation()
#             if not st_line.account_id and not journal_entries.ids and not st_line.statement_id.currency_id.is_zero(st_line.amount):
#                 raise UserError(_('All the account entries lines must be processed in order to close the statement.'))
#         moves = statement.mapped('line_ids.journal_entry_ids.move_id')
#         if moves:
#             moves.filtered(lambda m: m.state != 'posted').post()
#         statement.message_post(body=_('Statement %s confirmed, journal items were created.') % (statement.name,))
#     statements.write({'state': 'confirm', 'date_done': time.strftime("%Y-%m-%d %H:%M:%S")})
#
#
#     # self.ldate = datetime.now()
