from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ReportForAllcustom(models.TransientModel):
    _name = "report.overtime.and.delay.and.absence.c"

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date to')
    employee_for_all = fields.Many2one('hr.employee')

    @api.onchange('specific_date')
    def computeTorFff(self):
        for rec in self:
            if rec.specific_date == True:
                rec.specific_employee = False
                rec.employee_for_all = False

    @api.onchange('specific_employee')
    def computeTorF(self):
        for rec in self:
            if rec.specific_employee == True:
                rec.specific_date = False
                rec.date_from = False
                rec.date_to = False

    specific_employee = fields.Boolean(string="Specific Employee", default=False, store=True)
    specific_date = fields.Boolean(string="Specific Date", default=True, store=True)

    @api.depends('date_from', 'date_to')
    def see_d(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                    raise ValidationError(" Date To must be bigger than or Equal Date From ")

    @api.multi
    def get_report_all(self):
        self.sudo().see_d()
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'employee_for_all': self.employee_for_all.id,
                # 'code_test': self.code_test,
            },
        }
        print('data==', data)
        return self.env.ref('bi_hr_overtime_request.overtime_and_delay_and_absence_report').report_action(self, data=data)


class AllReportView(models.AbstractModel):
    _name = "report.bi_hr_overtime_request.overtime_and_delay_and_absence"
    _description = "overtime and delay and absence Report"


    @api.model
    def _get_report_values(self, docids, data=None):
        print("va"*5)
        docs = []
        domains = []
        if data['form']['employee_for_all']:
            # print('employee_loan id==', data['form']['employee_loan'])
            ove_id = self.env['overtime.request'].search([('employee_id', '=', data['form']['employee_for_all'])])
            print('MM=', ove_id)
            for rec in ove_id:
                docs.append({
                    'employee_name': rec.employee_id.name,
                    'depart_id': rec.department_id.name,
                    'start_d': rec.start_date,
                    'end_date': rec.end_date,
                    'month': rec.month_n,
                    'year': rec.year,
                    'num_of_hours': rec.num_of_hours,
                    'total_delay_hours': rec.total_delay_hours,
                })
            # www = {
            #     'doc_ids': data['ids'],
            #     'doc_model': data['model'],
            #     'employee_for_all': data['form']['employee_for_all'],
            #     'docs': docs,
            # }
            # print('www#=', www)
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'employee_for_all': data['form']['employee_for_all'],
                'docs': docs,
            }
        if data['form']['date_from'] or data['form']['date_to']:
            if data['form']['date_from'] and data['form']['date_to']:
                # print('d==', data['form']['date_from'], data['form']['date_to'])
                domains.append(('start_date', '>=', data['form']['date_from']))
                domains.append(('end_date', '<=', data['form']['date_to']))
            if data['form']['date_from'] and not data['form']['date_to']:
                domains.append(('start_date', '>=', data['form']['date_from']))
            if data['form']['date_to'] and not data['form']['date_from']:
                domains.append(('end_date', '<=', data['form']['date_to']))
            # domains = 3
            print('domain==', domains)
            ourloans = self.env['overtime.request'].search(domains, order='start_date asc')
            print('MM=', ourloans)
            for rec in ourloans:
                docs.append({
                    'employee_name': rec.employee_id.name,
                    'depart_id': rec.department_id.name,
                    'start_d': rec.start_date,
                    'end_date': rec.end_date,
                    'month': rec.month_n,
                    'year': rec.year,
                    'num_of_hours': rec.num_of_hours,
                    'total_delay_hours': rec.total_delay_hours,
                })
            # www={
            #     'doc_ids': data['ids'],
            #     'doc_model': data['model'],
            #     'date_from': data['form']['date_from'],
            #     'date_to': data['form']['date_to'],
            #     'docs': docs,
            # }
            # print('www#=', www)
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'date_from': data['form']['date_from'],
                'date_to': data['form']['date_to'],
                'docs': docs,
            }
