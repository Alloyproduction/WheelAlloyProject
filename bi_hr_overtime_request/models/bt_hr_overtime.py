# -*- coding: utf-8 -*-
import time
import calendar
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta, parser
from odoo import fields, api, models, _
from datetime import date, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, safe_eval


class BtHrOvertime(models.Model):
    _name = "bt.hr.overtime"
    _description = "Bt Hr Overtime"
    _rec_name = 'employee_id'
    _order = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    # manager_id = fields.Many2one('hr.employee', string='Manager')
    start_date = fields.Datetime('Check in')
    check_out_date = fields.Datetime('Check out')
    year = fields.Char('Year', store=True)
    month = fields.Char('Month', store=True)
    overtime_hours = fields.Float('Overtime Hours')
    delay_hours = fields.Float('Delay in Minute')
    # emp_req_d_h = fields.Float('Employee Request', store=True)
    overtime_hours2 = fields.Float('Overtime Hours')
    notes = fields.Text(string='Notes')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'),
                              ('validate', 'Approved'), ('cancel', 'Cancelled')], default='draft', copy=False)
    attendance_id = fields.Many2one('hr.attendance', string='Attendance')
    overtime_created = fields.Boolean(string='Overtime Created', default=True, copy=False)

    # fun for cron
    @api.model
    def run_overtime_and_delays_scheduler(self):
        attend_signin_ids = self.env['hr.attendance'].search([('overtime_created', '=', False)])
        tmp = 0
        for obj in attend_signin_ids:
            tmp = obj.id
            if obj.check_in and obj.check_out:
                print('check in day and time=', obj.check_in)
                print('idddd===', obj.id)
                c_date1 = obj.check_in.strftime('%m-%d-%Y')
                print('only date1', c_date1)
                if c_date1:
                    attend_signin2 = self.env['hr.attendance'].search([('overtime_created', '=', False)])
                    for r in attend_signin2:
                        print('id2=', r.id)
                        if r.check_in and r.check_out and obj.id != r.id and obj.employee_id.id == r.employee_id.id:
                            print('check2 in day and time=', r.check_in)
                            print('id22=', r.id)
                            other_date = r.check_in.strftime('%m-%d-%Y')
                            print('only date22=', other_date)
                            obj.TT_id = False
                            if c_date1 == other_date and obj.emp_req_d_h == 0:
                                obj.TT_id = True
                                obj.overtime_created = True
                                print('VVVVV')
                                pass
                                print('GGGG')
                #     myobj=self.env['hr.attendance'].search([('id', '=', obj.id)])
                #     print('PPPP',myobj.TT_id)
                    if obj.TT_id == False:
                        print('code here will be EX')
                        print('UUU', obj.id)
                        print('TTTT', tmp)
                        print('check out day and time=', obj.check_out)
                        current_time = obj.check_in.strftime("%H:%M:%S")
                        current_time_out = obj.check_out.strftime("%H:%M:%S")
                        h1 = str(current_time).split(':')[0]
                        h2 = str(current_time_out).split(':')[0]
                        m1 = str(current_time).split(':')[1]
                        m2 = str(current_time_out).split(':')[1]
                        total_h1_m1 = str(h1) + '.' + m1
                        total_h2_m2 = str(h2) + '.' + m2
                        contract_work_start = self.env['hr.contract'].search([('employee_id', '=', obj.employee_id.id)])
                        for rec in contract_work_start:
                            start_h = str(rec.start_hour)
                            h_s1 = start_h.split(':')[0]
                            m1_s = float(start_h) - float(h_s1)
                            end_h = str(rec.end_hour)
                            h2_e = end_h.split(':')[0]
                            m2_e = float(end_h) - float(h2_e)
                            # print('E=', h2_e, '.', m2_e)
                            # when employee come late am
                            if float(total_h1_m1) > float(start_h):
                                print('come late')
                                h_l = (int(h1) - float(h_s1)) * 60
                                m_l = int(m1) - float(m1_s)
                                h_m_l = h_l + m_l
                                delay_hours1 = float(h_m_l)
                                print('D NUM1#=',delay_hours1)
                            # when employee come on his time in am or less than
                            else:
                                print('come tmam')
                                delay_hours1 = 0
                            # when employee go home early
                            if float(total_h2_m2) < float(end_h):
                                print('leave early')
                                h_ll = (float(h2_e) - int(h2)) * 60
                                m_ll = float(m2_e) - int(m2)
                                h_m_ll = h_ll + m_ll
                                delay_hours2 = float(h_m_ll)
                                # print('duu=', delay_hours2)
                            else:
                                print('leave tmam')
                                delay_hours2 = 0
                        current_delay_hours = (delay_hours1 + delay_hours2) / 60
                        current_delay_hours_in_min = (delay_hours1 + delay_hours2)
                        hours_int = int(current_delay_hours_in_min)
                        print('qqqeee=', hours_int)
                        m2_int = current_delay_hours_in_min - hours_int
                        print('m222==', m2_int)
                        temp_id = 0
                        if obj.emp_req_d_h:
                            print('there are a employee req')
                            # convert employee req h to min
                            hours_req = int(obj.emp_req_d_h) * 60
                            print('qwwwww=', hours_req)
                            m7_int = (obj.emp_req_d_h - (hours_req / 60)) * 100
                            print('sssssssa==', m7_int)
                            total_hour_m_req = hours_req + m7_int
                            print('req T', total_hour_m_req)
                            # ____________________________________
                            print('delay req=', obj.emp_req_d_h)
                            print('rec delay id =', obj.id)
                            c_date = obj.check_in.strftime('%m-%d-%Y')
                            print('only date',c_date)
                            print('employee id=', obj.employee_id.id)
                            temp_id = obj.id # id = 13
                            search_rec = self.env['hr.attendance'].search([('overtime_created', '=', False),
                                                                           ('employee_id', '=', obj.employee_id.id),])
                            for s in search_rec:
                                print('iddddd',  s.id)
                                if temp_id == s.id: # id = 13
                                    print('#@@@@@')
                                    for rec in search_rec:
                                        print('rec=', rec)
                                        if temp_id == rec.id:
                                            print('emp leave in end of day')
                                            # pass
                                            print('total delay in an ou in all current day', current_delay_hours)
                                            delay_hours_after_req = (current_delay_hours_in_min - total_hour_m_req) / 60
                                            print('d_h=##', delay_hours_after_req)
                                            if delay_hours_after_req > 0:
                                                print('more than zerrrrrro++')
                                                delay_hours_after_req = delay_hours_after_req
                                            else:
                                                print('less than zerrro')
                                                delay_hours_after_req = 0
                                            print('^^^', delay_hours_after_req)
                                        else:
                                            print('other id')
                                            c_date2 = rec.check_in.strftime('%m-%d-%Y')
                                            print('only date##',c_date2)
                                            if c_date2 == c_date and obj.employee_id.id == rec.employee_id.id:
                                                print('$$$$$$$$$$$$')
                                                print('===========', c_date2 , c_date)
                                                print('check in1=', obj.check_in)
                                                print('check out1=', obj.check_out)
                                                print('check in2==', rec.check_in)
                                                print('check out2==', rec.check_out)
                                                # ____________________________________
                                                print('out==', float(total_h2_m2))
                                                # true time to come back again
                                                true_come_back = (total_hour_m_req / 60) + float(total_h2_m2)
                                                print('!!!', true_come_back)
                                                # the 2end check in
                                                print('come back at==', rec.check_in)
                                                come_back_at = rec.check_in.strftime("%H:%M:%S")
                                                h6 = str(come_back_at).split(':')[0]
                                                m6 = str(come_back_at).split(':')[1]
                                                total_h6_m6 = str(h6) + '.' + m6
                                                print('TT=', total_h6_m6)
                                                if float(total_h6_m6) > float(true_come_back):
                                                    print('emp come back mor than must be in')
                                                    delay1_w_emp_req = (float(total_h6_m6) - float(true_come_back))
                                                    if delay1_w_emp_req > 0:
                                                        print('> zerrro+')
                                                        delay1_w_emp_req = delay1_w_emp_req
                                                    else:
                                                        print('less than zerrrrrro')
                                                        delay1_w_emp_req = 0
                                                    print('D NUM2', delay1_w_emp_req)
                                                else:
                                                    delay1_w_emp_req = 0
                                            # when he leave eraly the delay will be calculated from last check out
                                                print('leave2 at==', rec.check_out)
                                                go_early = rec.check_out.strftime("%H:%M:%S")
                                                h8 = str(go_early).split(':')[0]
                                                m8 = str(go_early).split(':')[1]
                                                total_h8_m8 = str(h8) + '.' + m8
                                                print('TT=', total_h8_m8) # 16.0
                                                if float(total_h8_m8) < float(end_h):
                                                    print('leave early')
                                                    h_ll_req = (float(h2_e) - int(h8)) * 60
                                                    m_ll_req = float(m2_e) - int(m8)
                                                    h_m_ll_req = h_ll_req + m_ll_req
                                                    delay1_w_emp_req_lea = float(h_m_ll_req) / 60
                                                    print('D NUM3', delay1_w_emp_req_lea)
                                                else:
                                                    print('leave tmam when emp req for delay')
                                                    delay1_w_emp_req_lea = 0
                                                    print('D NUM3', delay1_w_emp_req_lea)
                                                print('D NUM3', delay1_w_emp_req_lea)
                                                delay_hours_after_req = delay1_w_emp_req_lea + delay1_w_emp_req + (delay_hours1 / 60)
                                                print('total late 1 and 2 and 3=', delay_hours_after_req)
                        # _________________________________
                        else:
                            print('no employee req')
                            delay_hours_after_req = current_delay_hours
                            print('2==', delay_hours_after_req)
                        delay_hours = delay_hours_after_req * 60
                        print('last total delay in min###', delay_hours)
                        print('end caluculate delaaaaaaaaaay')
                        start_date = datetime.datetime.strptime(obj.check_in.strftime('%Y-%m-%d %H:%M:%S'),
                                                                DEFAULT_SERVER_DATETIME_FORMAT)
                        print('start==', start_date)
                        start_day = obj.check_in.strftime('%A')
                        # print('start check in=', start_day)
                        end_date = datetime.datetime.strptime(obj.check_out.strftime('%Y-%m-%d %H:%M:%S'),
                                                              DEFAULT_SERVER_DATETIME_FORMAT)
                        print('end==', end_date)
                        difference = end_date - start_date
                        print('difference', difference)
                        # To calculate hour difference of an employee.
                        # It will calculate hour difference even if employee work more than 24 hours
                        hour_diff = int((difference.days) * 24 + (difference.seconds) / 3600)
                        print('hour_diff=', hour_diff)
                        min_diff = str(difference).split(':')[1]
                        print('min_diff', min_diff)
                        tot_diff = str(hour_diff) + '.' + min_diff
                        print('tot_diff', tot_diff)
                        actual_working_hours = float(tot_diff)
                        print('actual working hours', actual_working_hours)
                        contract_obj = self.env['hr.contract'].search([('employee_id', '=', obj.employee_id.id),
                                                                       ('work_hours', '!=', 0)])
                        for contract in contract_obj:
                            working_hours = contract.work_hours
                            print('w', working_hours)
                            if actual_working_hours > working_hours:
                                overtime_hours = actual_working_hours - working_hours
                                overtime_hours2 = overtime_hours
                                # print('ov2', overtime_hours2)
                                if start_day in ['Friday', 'Saturday']:
                                    overtime_hours2 *= 2
                                else:
                                    overtime_hours2 *= 1.5
                                # get Month and year from start_date
                                # print('ov =', overtime_hours)
                                # print('sd =', start_date)
                                current_start = str(start_date)
                                # print('current start=', current_start)
                                cur_d = current_start.split('-')
                                y, m, d = cur_d
                                # print('y=', y)
                                # print('m=', m)
                                vals = {
                                    'employee_id': obj.employee_id and obj.employee_id.id or False,
                                    'manager_id': obj.employee_id and obj.employee_id.parent_id and obj.employee_id.parent_id.id or False,
                                    'start_date': obj.check_in,
                                    'check_out_date': obj.check_out,
                                    'year': y,
                                    'month': m,
                                    'overtime_hours': round(overtime_hours, 2),
                                    'overtime_hours2': round(overtime_hours2, 2),
                                    'delay_hours': delay_hours,
                                    'attendance_id': obj.id,
                                }
                                self.env['bt.hr.overtime'].create(vals)
                                obj.overtime_created = True
                            else:
                                current_start = str(start_date)
                                cur_d = current_start.split('-')
                                y, m, d = cur_d
                                vals = {
                                    'employee_id': obj.employee_id and obj.employee_id.id or False,
                                    'manager_id': obj.employee_id and obj.employee_id.parent_id and obj.employee_id.parent_id.id or False,
                                    'start_date': obj.check_in,
                                    'check_out_date': obj.check_out,
                                    'year': y,
                                    'month': m,
                                    'overtime_hours': 0,
                                    'overtime_hours2': 0,
                                    'delay_hours': delay_hours,
                                    'attendance_id': obj.id,
                                }
                                self.env['bt.hr.overtime'].create(vals)
                                obj.overtime_created = True


    # @api.multi
    # def unlink(self):
    #     # for emp in self:
    #     #     if emp.overtime_created == True :
    #     #         raise UserError(_("you can`t delete this record until"
    #     #                           " go to attendance and remove check on overtime created "))
    #             # print('id=', self)
    #     res = super(BtHrOvertime, self).unlink()
    #     all_attend_signin_ids = self.env['hr.attendance'].search([('overtime_created', '=', False)])
    #             # print('return res = ', res)
    #     return res

    @api.multi
    def action_submit(self):
        return self.write({'state': 'confirm'})

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def action_approve(self):
        return self.write({'state': 'validate'})

    @api.multi
    def action_refuse(self):
        return self.write({'state': 'refuse'})

    @api.multi
    def action_view_attendance(self):
        attendances = self.mapped('attendance_id')
        action = self.env.ref('hr_attendance.hr_attendance_action').read()[0]
        if len(attendances) > 1:
            action['domain'] = [('id', 'in', attendances.ids)]
        elif len(attendances) == 1:
            action['views'] = [(self.env.ref('hr_attendance.hr_attendance_view_form').id, 'form')]
            action['res_id'] = self.attendance_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def create_ov_r(self):
        all_employee_ids = self.env['hr.employee'].search([])
        for employee in all_employee_ids:
            # print('E Name', employee.name)
            ova_obj = self.env['bt.hr.overtime'].read_group([('employee_id', '=', employee.id)],
                                                            fields=['overtime_hours', 'employee_id', 'start_date',
                                                                    'overtime_hours2', 'delay_hours'],
                                                            groupby=['start_date'], lazy=False)
            # print('=============================')
            # print(ova_obj)
            months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7,
                      'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
            for line in ova_obj:
                # print('s====', line['start_date'])
                # print(line)
                # print('em', line.employee_id.id)
                # print(line['overtime_hours'])
                # print(line['start_date'])
                mt = line['start_date'].split(' ')
                # print('start date=',mt)
                # print(months[mt[0]])
                m = months[mt[0]]
                m_n = mt[0]
                # print('m_n =' ,m_n)
                # print('Month =' ,m)
                # print(mt[1])
                y = mt[1]
                # print('y===', y)
                s = line['start_date']
                # print('s=', s)
                # first day in all current months
                first_day = parser.parse(s) + relativedelta.relativedelta(day=1)
                first_day_only_date = first_day.strftime('%m-%d-%Y')
                # print('first_day_only_date', first_day_only_date)
                # o_d = only_date[0]
                # print('only date', o_d)
                # print('first_day =', first_day)
                last_day = parser.parse(s) + relativedelta.relativedelta(months=+1, day=1, days=-1)
                last_day_only_date = last_day.strftime('%m-%d-%Y')
                # print('last_day only date =', last_day_only_date)
                # print('last_day =', last_day)
                # overtime_hours
                x = line['overtime_hours']
                x2 = line['overtime_hours2']
                x3 = line['delay_hours'] - 60
                print('x2=', x2)
                # print(line['__domain'][4][2])
                record = self.env['overtime.request'].search([('employee_id', '=', (line['__domain'][4][2])),
                                                              ('month', '=', m), ('year', '=', y)])

                # print('record =', record)
                if record:
                    pass
                else:
                    # print("creat")
                    # print('other R', record)
                    self.env['overtime.request'].create({
                        'employee_id': employee.id,
                        # 'employee_id': employee.name,
                        'num_of_hours': x,
                        'num_of_hours2': x2,
                        'total_delay_hours': x3,
                        'month': m,
                        'month_n': m_n,
                        'year': y,
                        'start_date': first_day_only_date,
                        'end_date': last_day_only_date,
                    })


class Contract(models.Model):
    _inherit = 'hr.contract'

    work_hours = fields.Float(string='Working Hours')
    # start_hour = fields.Float(string='start hour')
    # start_hour = fields.Datetime(string='Start Working Hours', default=lambda self: fields.datetime.now())
    start_hour = fields.Float(string='Start Working Hours', required=True, index=True)
    end_hour = fields.Float(string='End Working Hours', required=True, index=True)

    # start_hour = fields.datetime.now().time()
    # start_work_h = fields.datetime('Work Start At', required=False, )

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    overtime_created = fields.Boolean(string='Overtime Created', default=False, copy=False)
    emp_req_d_h = fields.Float('Employee request for a delay')
    TT_id = fields.Boolean()

class hr_employee(models.Model):
    _inherit = 'hr.employee'
