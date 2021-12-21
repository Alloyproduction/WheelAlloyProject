from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ReportForLoan(models.TransientModel):
    _name = "report.loan.c"

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date to')
    employee_loan = fields.Many2one('hr.employee')

    # @api.depends('specific_employee', 'specific_date')
    @api.onchange('specific_date')
    def computeTorFff(self):
        for rec in self:
            if rec.specific_date == True:
                rec.specific_employee = False
                rec.employee_loan = False

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
    def get_loan_report(self):
        self.sudo().see_d()
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'employee_loan': self.employee_loan.id,
            },
        }
        return self.env.ref('dev_hr_loan.loans_report').report_action(self, data=data)


class LoanReportView(models.AbstractModel):
    _name = "report.dev_hr_loan.loans_report_view"
    _description = "Loans Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        print("values"*5)
        docs = []
        domains = []
        if data['form']['employee_loan']:
            # print('employee_loan id==', data['form']['employee_loan'])
            ourloans_id = self.env['employee.loan'].search([('employee_id', '=', data['form']['employee_loan'])])
            # print('MM=', ourloans_id)
            for rec in ourloans_id:
                docs.append({
                    'date': rec.date,
                    'reference': rec.name,
                    'employee_name': rec.employee_id.name,
                    'depart_id': rec.department_id.name,
                    # 'mang_id': rec.manager_id.name,
                    'j_id': rec.job_id,
                    'loan_type': rec.loan_type_id.name,
                    'l_am': round(rec.loan_amount, 2),
                    'start_d': rec.start_date,
                    'num_terms': rec.term,
                    'pa_amount': round(rec.paid_amount, 2),
                    'rema_amount': round(rec.remaing_amount, 2),
                    'install_amount': round(rec.installment_amount, 2),
                    'state_loann': rec.state,
                })
            # www = {
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
        if data['form']['date_from'] or data['form']['date_to']:
            if data['form']['date_from'] and data['form']['date_to']:
                # print('d==', data['form']['date_from'], data['form']['date_to'])
                domains.append(('date', '>=', data['form']['date_from']))
                domains.append(('date', '<=', data['form']['date_to']))
            if data['form']['date_from'] and not data['form']['date_to']:
                domains.append(('date', '>=', data['form']['date_from']))
            if data['form']['date_to'] and not data['form']['date_from']:
                domains.append(('date', '<=', data['form']['date_to']))

            # domains = 3
            # print('domain==', domains)
            ourloans = self.env['employee.loan'].search(domains, order='date asc')
            # print('MM=', ourloans)
            for rec in ourloans:
                docs.append({
                    'date': rec.date,
                    'reference': rec.name,
                    'employee_name': rec.employee_id.name,
                    'depart_id': rec.department_id.name,
                    # 'mang_id': rec.manager_id.name,
                    'j_id': rec.job_id,
                    'loan_type': rec.loan_type_id.name,
                    'l_am': round(rec.loan_amount, 2),
                    'start_d': rec.start_date,
                    'num_terms': rec.term,
                    'pa_amount': round(rec.paid_amount, 2),
                    'rema_amount': round(rec.remaing_amount, 2),
                    'install_amount': round(rec.installment_amount, 2),
                    'state_loann': rec.state,
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
