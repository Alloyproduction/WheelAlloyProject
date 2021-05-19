from odoo import models, fields, api


class SalaryCustomerReportWizard(models.TransientModel):
    _name = 'salary.report.wizard'


    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date", default=fields.Date.today)
    print_all = fields.Boolean()


    def get_salary_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'print_all': self.print_all,
            },
        }
        return self.env.ref('hr_management_system.salary_report_report').report_action(self, data=data)


class SalaryCustomerReportReportView(models.AbstractModel):
    _name = "report.hr_management_system.salary_report_report_view"
    _description = "Salary Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        domains = []
        if data['form']['start_date'] :
            domains.append(('date_from', '>=', data['form']['start_date']))
            domains.append(('date_to', '<=', data['form']['end_date']))

        payrolls = self.env['hr.payslip'].search(domains, order='name asc')

        if data['form']['print_all']:
            payrolls = self.env['hr.payslip'].search([], order='name asc')

        for payroll in payrolls:
            # employee_id is m2o field, it was calling the ID of the record, not the name, this code below calling the name.
            # employee_id = dict(payroll._fields['employee_id'].selection).get(payroll.employee_id)
            docs.append({
                'start_date': data['form']['start_date'],
                'end_date': data['form']['end_date'],
                'employee_id': payroll.employee_id.name,
                'number': payroll.number,
                'name': payroll.name,
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': data['form']['start_date'],
            'date_end': data['form']['end_date'],
            'docs': docs,
        }
