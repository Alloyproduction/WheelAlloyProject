# -*- coding: utf-8 -*-
""" HR Payroll Batch Journal Entry """

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    batch_date = fields.Date('Date Account', states={'draft': [('readonly',
                                                                False)]},
                             readonly=True,
                             help="Keep empty to use the period of the validation("
                                  "Batch) date To.", default=lambda self: fields.Date.to_string( (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    batch_move_id = fields.Many2one('account.move', 'Accounting Entry',
                                    readonly=True, copy=False)

    # @api.constrains("journal_id", "slip_ids", "slip_ids.company_id")
    # def _check_same_company(self):
    #     for slip in self.slip_ids:
    #         if slip.company_id != self.company_id:
    #             raise ValidationError(_(
    #                 'The payslip of employee (%s) must belong to the same '
    #                 'company(%s) in journal (%s).') %
    #                                   slip.employee_id.name,
    #                                   self.journal_id.company_id.name,
    #                                   self.journal_id.name)

    def _get_draft_payslips(self, payslips):
        """
        @param payslips: recordset of payslips
        @:return recordset of payslips not validated
        """
        self.ensure_one()
        return payslips.filtered(lambda x: x.state not in ["done", "cancel"])

    @api.multi
    def draft_payslip_run(self):
        moves = self.mapped('batch_move_id')
        moves.filtered(lambda x: x.state == 'posted').button_cancel()
        moves.unlink()
        for rec in self:
            rec._set_payslip_draft()
        return super(HrPayslipRun, self).draft_payslip_run()


    @api.multi
    def _set_payslip_draft(self):
        for rec in self:
            for slip in rec.slip_ids:
                if slip.state == "done":
                    slip.write({'state': 'draft'})
                    if slip.move_id:
                        slip.move_id.button_cancel()
                        slip.move_id.unlink()

    @api.multi
    def close_payslip_run(self):
        super(HrPayslipRun, self).close_payslip_run()
        for rec in self:
            if rec.batch_move_id:
                raise UserError(_("You cannot close a payslip batch that is "
                                  "not in "
                                  "draft."))
            payslips = rec._get_draft_payslips(rec.slip_ids)
            if payslips:
                for payslip in payslips:
                    payslip.compute_sheet()
                rec._create_batch_move(payslips)

    def _create_batch_move(self, payslips):
        self.ensure_one()
        currency = self.journal_id.currency_id or \
                   self.journal_id.company_id.currency_id
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        date = self.batch_date or self.date_end
        name = _("Payslip Batch of %s") % self.name
        move_dict = {
            'narration': name,
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'date': date,
        }
        for slip in payslips:
            slip.write({'state': 'done'})
            for line in slip.details_by_salary_rule_category:
                amount = round(currency.round(
                    self.credit_note and -line.total or line.total) ,2)
                print("amount2344 ",amount)
                if currency.is_zero(amount):
                    continue
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:
                    debit = amount > 0.0 and amount or 0.0
                    debit = currency.round(debit)
                    credit = amount < 0.0 and -amount or 0.0
                    credit = currency.round(credit)

                    city =line.slip_id.contract_id.city_id.id
                    analytic=None
                    if line.slip_id.contract_id.analytic_tags_id:
                        analytic = line.slip_id.contract_id.analytic_tags_id.ids[0]

                    debit_line = self._get_existing_lines(
                        line_ids, line, debit_account_id, debit, credit, city , analytic)
                    print("de" , debit_line)
                    if not debit_line :
                        debit_line = (0, 0, {
                            'name': line.name ,
                            # 'partner_id': line._get_partner_id(
                                # credit_account=False),
                            'account_id': debit_account_id,
                            'journal_id': self.journal_id.id,
                            'city_id' : line.slip_id.contract_id.city_id.id,
                            'date': date,
                            'debit': debit,
                            'credit': credit,
                            'analytic_account_id': line.slip_id.contract_id.analytic_account_id.id,
                             'analytic_tag_ids':[(6, 0,  line.slip_id.contract_id.analytic_tags_id.ids)]   ,
                            'tax_line_id': line.salary_rule_id.account_tax_id.id,
                        })
                        line_ids.append(debit_line)

                    else :
                        debit_line[2]['debit'] += debit
                        debit_line[2]['credit'] += credit

                    # debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
                    debit_sum += debit_line[2]['debit']
                #
                if credit_account_id:

                    debit = amount < 0.0 and -amount or 0.0
                    debit = currency.round(debit)
                    credit = amount > 0.0 and amount or 0.0
                    credit = currency.round(credit)
                    city = line.slip_id.contract_id.city_id.id
                    analytic = None
                    if line.slip_id.contract_id.analytic_tags_id:
                        analytic = line.slip_id.contract_id.analytic_tags_id.ids[0]

                    credit_line = self._get_existing_lines(
                        line_ids, line, credit_account_id, debit, credit,city , analytic)
                    print("de", credit_line)
                    if not  credit_line:

                        credit_line = (0, 0, {
                            'name': line.name,
                            # 'partner_id': line._get_partner_id(credit_account=True),
                            'account_id': credit_account_id,
                            'journal_id': self.journal_id.id,
                            'city_id': line.slip_id.contract_id.city_id.id,
                            'date': date,
                            'debit': debit,
                            'credit': credit,
                            'analytic_account_id':  line.slip_id.contract_id.analytic_account_id.id,
                            'analytic_tag_ids': [(6, 0,  line.slip_id.contract_id.analytic_tags_id.ids)]  ,
                            'tax_line_id': line.salary_rule_id.account_tax_id.id,
                        })
                        line_ids.append(credit_line)
                    else:
                        credit_line[2]['debit'] += debit
                        credit_line[2]['credit'] += credit

                    # credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
                    credit_sum += credit_line[2]['credit']

        print("debit sum" , debit_sum)
        print("debit sum" , credit_sum)
        debit_sum1 = 0
        credit_sum1 = 0
        for line_id in line_ids:  # Get the debit and credit sum.
            debit_sum1 += line_id[2]['debit']
            credit_sum1 += line_id[2]['credit']
        # debit_sum1 = currency.round(debit_sum1)
        # credit_sum1 = currency.round(credit_sum1)
        print(debit_sum1)
        print(credit_sum1)

        if currency.compare_amounts(credit_sum1, debit_sum1) == -1:
            acc_id = self.journal_id.default_credit_account_id.id
            if not acc_id:
                raise UserError(_(
                    'The Expense Journal "%s" has not properly configured the Credit Account!') % (
                                    self.journal_id.name))
            adjust_credit = (0, 0, {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': 0.0,
                'credit': currency.round(debit_sum1 - credit_sum1),
            })
            line_ids.append(adjust_credit)
        elif currency.compare_amounts(debit_sum1, credit_sum1) == -1:
            acc_id = self.journal_id.default_debit_account_id.id
            if not acc_id:
                raise UserError(_(
                    'The Expense Journal "%s" has not properly configured the Debit Account!') % (
                                    self.journal_id.name))
            adjust_debit = (0, 0, {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': currency.round(credit_sum1 - debit_sum1),
                'credit': 0.0,
            })
            line_ids.append(adjust_debit)
        print("hh",line_ids)
        move_dict['line_ids'] = line_ids
        # if move_dict:
        move = self.env['account.move'].create(move_dict)
        self.write({'batch_move_id': move.id, 'batch_date': date})
            # move.post()


    def _get_existing_lines(self, line_ids, line, account_id, debit, credit , city , analytical_account):

        for line_id in line_ids :
            if city and city != None and  analytical_account and analytical_account != None :
                if  line_id[2]['name'] == line.name and line_id[2]['account_id'] == account_id \
                    and  line_id[2]['city_id'] == city \
                        and   line_id[2]['analytic_account_id'] ==  analytical_account :
                    print(line.name)
                    print(city)
                    print(analytical_account)
                    print(" line ", line)
                    return line_id
            # elif city and city != None  :
            #     if line_id[2]['account_id'] == account_id \
            #             and line_id[2]['city_id'] == city :
            #
            #         return line_id
            # elif  analytical_account and analytical_account != None :
            #     if  line_id[2]['account_id'] == account_id \
            #             and line_id[2]['analytic_account_id'] == analytical_account:
            #         return line_id
            else :
                if line_id[2]['name'] == line.name and line_id[2]['account_id'] == account_id :
                    print(line.name)
                    print(account_id)
                    return line_id
            print("last",line.name)
        return False


#and line_id[2]['analytic_account_id'] == (line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id)  \
                    # and ((line_id[2]['debit'] > 0 and credit <= 0) or (line_id[2]['credit'] > 0 and debit <= 0)) :