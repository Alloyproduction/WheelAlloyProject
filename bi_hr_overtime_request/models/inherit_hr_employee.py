# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError


class Hr_employee_inherit_(models.Model):
    _inherit = "hr.employee"

    # fun for overtime rule
    @api.multi
    def get_overtime(self, id, start_date, end_date):
        over_time_rec = self.env['overtime.request'].search([('employee_id', '=', id), ('start_date', '>=', start_date),
                                                             ('end_date', '<=', end_date), ('state', '=', 'done')])

        # print('o', over_time_rec)
        my_con = self.env['hr.contract'].search([('employee_id', '=', id)])
        # print('my con', my_con.wage)
        price_hour = my_con.wage / (30*8)
        # print('price h  =', price_hour)
        total = price_hour
        for line in over_time_rec:
            if line.include_in_payroll == True:
                total = total * line.num_of_hours2
                # print('total =', total)
                # print ('line h', line.num_of_hours2)
        multi_over_time_rec = self.env['multiple.overtime.request'].search([('start_date', '>=', start_date),
                                                                            ('end_date', '<=', end_date),
                                                                            ('state', '=', 'done')])
        for res in multi_over_time_rec:
            if res.include_in_payroll == True:
                if id in res.employee_ids.ids:
                    total = total + res.num_of_hours
                    # print('total 2=',total)
        return total

    # fun for delay rule
    @api.multi
    def get_delay(self, id, start_date, end_date):
        delay_rec = self.env['overtime.request'].search([('employee_id', '=', id), ('start_date', '>=', start_date),
                                                             ('end_date', '<=', end_date), ('state', '=', 'done')])
        # print('delay_r', delay_rec)
# ----------------------------------------------
#         print('BBBBBBBBBBB')
        my_con = self.env['hr.contract'].search([('employee_id', '=', id)])
        # Delays for employees
        price_for_minute = (my_con.wage / (30 * 8)) / 60
        # print('M=0=', price_for_minute)
        # print('price h  =', price_hour)
        result = price_for_minute
        # print('price for M', result)
        for line in delay_rec:
            if line.include_in_payroll == True:
                print('000000000')
                print('total delay h=', line.total_delay_hours)
                delay_h_and_m = line.total_delay_hours
                print('total delay h===', delay_h_and_m)
                h2 = int(delay_h_and_m)
                print('hh=', h2)
                m2 = delay_h_and_m - h2
                print('mm=', m2)
                print('qqww', (( h2 * 60) + ( m2* 100)))
                result = result * (delay_h_and_m * 60)
                print('re==', result)
        return result
