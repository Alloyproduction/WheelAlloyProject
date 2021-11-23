# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from datetime import datetime, date
import datetime
from odoo.addons import decimal_precision as dp
import numpy as np


class EndOfServiceAward(models.Model):
    _name = 'end.of.service.award'
    _description = 'End of Service Award'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, index=True, tracking=True,
                                  track_visibility='onchange')
    contract_id = fields.Many2one('hr.contract', string='Contract', domain="[('employee_id', '=', employee_id)]",
                                  tracking=True, copy=False, related='employee_id.contract_id')
    join_date = fields.Date(string="Join Date", related='employee_id.join_date', tracking=True)
    last_work_date = fields.Date(tracking=True, default=date.today())
    contact_end_type = fields.Selection([('end_period', 'End of Contract Period'),
                                         ('immediate_resignation', 'Immediate resignation'),
                                         ('resignation_after_month', 'Resignation After Month'),
                                         ('law_80', 'Law 80'),
                                         ],
                                        default='end_period', tracking=True)

    number_of_days_from_join_date = fields.Float(string="Number of Days From Join Date",
                                                 compute='_compute_number_of_days_from_join_date', tracking=True)
    first_period_days = fields.Float(compute='_compute_number_of_days_from_join_date', tracking=True)
    second_period_days = fields.Float(compute='_compute_number_of_days_from_join_date', tracking=True)
    total_unpaid_days = fields.Float(string='Total Unpaid Days First Period', compute='_compute_total_unpaid_days')
    total_unpaid_days_second_period = fields.Float(compute='_compute_total_unpaid_days')
    net_period = fields.Float(compute='_compute_all_net_period')
    net_first_period = fields.Float(compute='_compute_all_net_period')
    net_second_period = fields.Float(compute='_compute_all_net_period')
    total_days_before = fields.Float(string="Total Years Before Five Years")
    total_days_after = fields.Float(string="Total Years After Five Years")
    net_period_before_5year = fields.Float(string="Deserve First Period", compute='_compute_total_years')
    net_period_after_5year = fields.Float(string="Deserve Second Period", compute='_compute_total_years')
    total_deserve = fields.Float(string="Total Deserve", compute='_compute_total_years')
    total_deserved_per_contract_end_type = fields.Float(compute='_compute_final_deserving')
    final_deserving = fields.Float(string="Final Deserving", compute='_compute_final_deserving')
    # eos_computation_dependency = fields.Html()
    # holiday_days = fields.Float(compute='_compute_holiday_days', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved')
    ], string='Status', readonly=True, tracking=True, copy=False, default='draft')

    @api.depends('employee_id')
    def _compute_total_unpaid_days(self):
        leave = 0.0
        leave_first_period = 0.0
        leave_second_period = 0.0
        for rec in self:
            if rec.employee_id:
                leave_ids = self.env['hr.leave']
                company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
                no_of_days_in_first_period = company.first_period * company.no_of_days_per_year
                end_date_first_period = self.join_date + timedelta(days=no_of_days_in_first_period)
                leave_id = company.leave_id
                leave_obj_id = leave_ids.search([('employee_id', '=', rec.employee_id.id),
                                                 ('state', '=', 'validate'),
                                                 ('holiday_status_id', '=', leave_id.id)])
                if leave_obj_id:
                    for l in leave_obj_id:
                        if l.request_date_to <= end_date_first_period:
                            leave_first_period += l.number_of_days
                        else:
                            leave_second_period += l.number_of_days
        self.total_unpaid_days = leave_first_period
        self.total_unpaid_days_second_period = leave_second_period

    @api.depends('join_date', 'last_work_date')
    def _compute_number_of_days_from_join_date(self):
        for record in self:
            record.number_of_days_from_join_date = 0
            record.first_period_days = 0
            record.second_period_days = 0
            if record.last_work_date and record.join_date:
                number_of_days_from_join_date = record.last_work_date - record.join_date

                company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
                no_of_days_in_first_period = company.first_period * company.no_of_days_per_year

                if number_of_days_from_join_date.days > no_of_days_in_first_period:
                    first_period_days = no_of_days_in_first_period
                    second_period_days = number_of_days_from_join_date.days - no_of_days_in_first_period
                else:
                    first_period_days = number_of_days_from_join_date.days
                    second_period_days = 0.0
                record.first_period_days = first_period_days
                record.second_period_days = second_period_days
                record.number_of_days_from_join_date = number_of_days_from_join_date.days

    @api.depends('number_of_days_from_join_date', 'total_unpaid_days')
    def _compute_all_net_period(self):
        for record in self:
            company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            record.net_first_period = (record.first_period_days - record.total_unpaid_days) / company.no_of_days_per_year
            # print('net_first_period',record.net_first_period, 'first_period_days',record.first_period_days)
            # print('total_unpaid_days',record.total_unpaid_days, 'no_of_days_per_year',company.no_of_days_per_year)
            record.net_second_period = (record.second_period_days - record.total_unpaid_days_second_period) / company.no_of_days_per_year
            # print('net_second_period',record.net_second_period, 'second_period_days',record.second_period_days)
            # print('total_unpaid_days_second_period', record.total_unpaid_days_second_period, 'no_of_days_per_year', company.no_of_days_per_year)
            record.net_period = round(record.net_first_period, 3) + round(record.net_second_period, 3)
            # print('net_period', record.net_period)

    @api.depends('net_first_period', 'net_second_period')
    def _compute_total_years(self):
        for record in self:
            company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            no_of_days_per_year = company.no_of_days_per_year
            first_period = company.first_period
            deserve_first_period = record.net_first_period * 15
            deserve_second_period = round(record.net_second_period * 30, 2)
            # print('SP=', deserve_second_period)
            self.net_period_before_5year = deserve_first_period
            self.net_period_after_5year = deserve_second_period
            record.total_deserve = deserve_first_period + deserve_second_period

    @api.depends('total_deserve', 'contact_end_type', 'number_of_days_from_join_date')
    def _compute_final_deserving(self):
        self.eos_computation_dependency = False
        company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
        no_of_days_per_year = company.no_of_days_per_year
        total_years = self.number_of_days_from_join_date / no_of_days_per_year
        total_deserved_per_contract_end_type = 0.0
        for record in self:
            if record.contact_end_type == 'end_period':
                total_deserved_per_contract_end_type = record.total_deserve
            elif record.contact_end_type in ['immediate_resignation', 'resignation_after_month']:
                if total_years < 2:
                    total_deserved_per_contract_end_type = 0.0
                elif 2 <= total_years < 5:
                    total_deserved_per_contract_end_type = record.total_deserve/3
                elif 5 <= total_years < 10:
                    total_deserved_per_contract_end_type = (record.total_deserve) * (2/3)
                else:
                    total_deserved_per_contract_end_type = record.total_deserve
            else:
                total_deserved_per_contract_end_type = 0.0
        contract = self.env['hr.contract'].browse(self.contract_id.id)
        self.total_deserved_per_contract_end_type = total_deserved_per_contract_end_type
        # self.final_deserving = total_deserved_per_contract_end_type * ((contract.wage + contract.conv_allowance + contract.travel_allowance) / 30)
        self.final_deserving = total_deserved_per_contract_end_type * ((contract.new_total + contract.travel_allowance) / 30)
        # print('final_deserving', self.final_deserving)
        # print('total_deserved_per_contract_end_type', total_deserved_per_contract_end_type)
        # print('wage', contract.wage)
        # print('contract.conv_allowance', contract.conv_allowance)
        # print('contract.travel_allowance', contract.travel_allowance)

    def action_approve(self):
        self.state = "approved"

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('You Can Not Delete a Request Which Is Not Draft.'))
            res = super(EndOfServiceAward, record).unlink()
            return res

    def get_day_name_from_date(self, contract_day):
        contract_day = str(contract_day)
        year, month, day = contract_day.split('-')
        day_name = datetime.date(int(year), int(month), int(day))
        e_name = day_name.strftime("%A")
        if e_name == 'Saturday':
            ar_name = 'السبت'
        elif e_name == 'Sunday':
            ar_name = 'الاحد'
        elif e_name == 'Monday':
            ar_name = 'الاثنين'
        elif e_name == 'Tuesday':
            ar_name = 'الثلاثاء'
        elif e_name == 'Wednesday':
            ar_name = 'الاربعاء'
        elif e_name == 'Thursday':
            ar_name = 'الخميس'
        else:
            ar_name = 'الجمعه'
        return ar_name


    @api.constrains('employee_id')
    def _check_record(self):
        for rec in self:
            domain = [
                ('employee_id', '=', rec.employee_id.id),
                ('id', '!=', rec.id),
            ]
            records = self.search_count(domain)
            # print('KKKKKKKK',records)
            if records:
                raise ValidationError(_('You can not have two record for the same employee'))


class Hr_employee_inherit_(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def get_total_end(self, id):
        my_con = self.env['end.of.service.award'].search([('employee_id', '=', id)])
        print('my final_deserving', my_con.final_deserving)
        result = my_con.final_deserving
        return result

    @api.multi
    def get_total_end_show_only_in_payroll(self, id):
        my_con = self.env['hr.contract'].search([('employee_id', '=', id)])
        result = 0
        print('my con wage', my_con.wage)
        print('my con new_total', my_con.new_total)
        last_work_date = datetime.date.today()
        print('cur_date1', last_work_date)
        # join_date = my_con['date_start']
        our_employee = self.env['hr.employee'].search([('id', '=', id)])
        # print('our_employee==', our_employee)
        print('qqqq' * 10)
        join_date = our_employee['join_date']
        # if join_date == False:
        #     print('fa' * 10)
        #     raise ValidationError(_('Set Join Date for this employee'))
        # else:
        print('join_date' , join_date)
        print('else' * 10)
        # print('join_date==', join_date)
        diff = last_work_date - join_date
        # print('diff =', diff.days)
        all_years = diff.days / 365
        # print('all years', all_years)
        # emp_wage = my_con.wage
        if all_years > 5:
            # first_period = 5 * 15
            # print('first_period', first_period)
            # second_period = (all_years - (first_period / 15)) * 30
            # print('second_period', second_period)
            result = (my_con.new_total / 12)
        else:
            # first_period = all_years * 15
            # result = ((my_con.wage / 30) * first_period)
            # second_period = 0.0
            result = (((my_con.new_total / 30) * 15) / 12)
        # total_deserve_period = first_period + second_period
        # print('total_deserve_period', total_deserve_period)
        # result = ((my_con.wage / 30) * total_deserve_period) / 12
        # print('all result', result)
        # print('all result', result)
        # return result
        return result


class HrPayslipLineInherit(models.Model):
    _inherit = 'hr.payslip.line'


class HrPayslipCustom(models.Model):
    _inherit = 'hr.payslip'

    # amount = fields.Float(string='HHH', digits=dp.get_precision('Payroll'),  store=True)

    # @api.depends('line_ids')
    # @api.onchange('line_ids')
    def onchange_amount_other(self):
        for line in self:
            if line.line_ids:
                for l in line.line_ids:
                    # print('ss3 ' * 7), print(l.name, l.code, l.category_id.id)
                    # print(l.salary_rule_id.id, l.amount), print('done' * 7)
                    se_rule = self.env['hr.salary.rule'].search([('id', '=', l.salary_rule_id.id),
                                                                 ('category_id.id', '=', l.category_id.id),
                                                                 ('name', '=', 'Other Salary'), ('code', '=', 'OTHER')])
                    # print('se_rule', se_rule ,'se_rule==', len(se_rule))
                    if se_rule:
                        for am in se_rule:
                            # print('am.amount_fix111==', am.amount_fix, 'l.amount111==', l.amount)
                            am.amount_fix = l.amount

    def write(self, vals):
        res = super(HrPayslipCustom, self).write(vals)
        # print('$$' * 5)
        self.onchange_amount_other()
        # print('qqq' * 5)
        return res
