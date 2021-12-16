from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import request
import base64
import io


class ReportForLoan(models.TransientModel):
    _name = "report.crm.custom"
    # _name = "report.loan.c"

    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date to', required=True)
    partner_id = partner_id = fields.Many2one('res.partner', index=True)
    stage_select = fields.Many2many('crm.stage', string="Stage")


    @api.depends('date_from', 'date_to')
    def see_d(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                    raise ValidationError(" Date To must be bigger than or Equal Date From ")

    @api.multi
    def get_crm_report(self):
        # print("get loan"*5)
        self.sudo().see_d()
        # print("selff"*5)
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }
        # print('data', data)
        return self.env.ref('alloy_crm_modification.crm_report').report_action(self, data=data)



    @api.multi
    def get_crm_repor_pdft(self):
        # print("get loan"*5)
        self.sudo().see_d()
        # print("selff"*5)
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }
        # print('data', data)
        return self.env.ref('alloy_crm_modification.crm_report_pdf').report_action(self, data=data)

#########################################################################################################################################

# class LoanReportView(models.AbstractModel):
class crmReportViewxls(models.AbstractModel):
    # _name = "report.dev_hr_loan.loans_report_view"
    _name = "report.alloy_crm_modification.crm_report"
    _inherit = 'report.report_xlsx.abstract'
    _description = "crm XLX Report"


    def _generate_xlsx_report(self, workbook, data, lines ):
        # print('test', data['a'])
        name = data['record']
        # user_obj = self.env['res.users'].search([('id', '=', data['context']['uid'])])
        # wizard_record = request.env['report.crm.custom'].search([])[-1]
        task_obj = request.env['crm.lead']
        # users_selected = []
        # stages_selected = []
        # if wizard_record.partner_select:
        #     if wizard_record.stage_select:
        current_task = task_obj.search([('partner_id', '=', name)])
                                        # ('user_id', 'in', users_selected),
                                        # ('stage_id', 'in', stages_selected)])
        vals = []
        for i in current_task:
            vals.append({
                'name': i.name,
                'user_id': i.partner_id,
                'stage_id': i.stage_id,
            })

        sheet = workbook.add_worksheet('leads')
        bold = workbook.add_format({'bold': True})
        # format_1 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'yellow'})
        sheet.set_column('A:D', 14)
        # row = 1
        # col = 1

        sheet.write(1, 1, 'Lead Name', bold)
        sheet.write(1, 2, 'email', bold)
        sheet.write(1, 2, 'Date', bold)
        # for lead1 in data['lead']:
         # row += 1

        # sheet.write(2, 1,lead1['partner_id'],format_1)
        # sheet.write(2, 2, lead1['email_from'],format_1)
        # # sheet.write(2, 3, lead1['phon'])


#################################################################################################################################################

class crmReportViewpdf(models.AbstractModel):
         _name = "report.alloy_crm_modification.crm_report_pdf"
         _description = "CRM PDF Report"

         @api.model
         def _get_report_values(self, docids, data=None):
             print("values" * 5)
             docs = []
             domains = []
             if data['form']['date_from'] and data['form']['date_to']:
                 print('d==', data['form']['date_from'], data['form']['date_to'])
                 domains.append(('date_deadline', '>=', data['form']['date_from']))
                 domains.append(('date_deadline', '<=', data['form']['date_to']))
             if data['form']['date_from'] and not data['form']['date_to']:
                 domains.append(('date_deadline', '>=', data['form']['date_from']))
             if data['form']['date_to'] and not data['form']['date_from']:
                 domains.append(('date_deadline', '<=', data['form']['date_to']))
             print('domain==', domains)
             ourloans = self.env['crm.lead'].search(domains, order='date asc')
             print('MM=', ourloans)
             for rec in ourloans:
                 docs.append({
                     'date': rec.date_deadline,
                     'name': rec.partner_id.name,
                     'car_type': rec.car_type_id,
                     'phone': rec.phone,
                     'location': rec.city_id,
                     'inquiry': rec.call_reason,
                     'source': rec.crm_source_id,
                     # 'depart_id': rec.department_id.name,
                     # # 'mang_id': rec.manager_id.name,
                     # 'j_id': rec.job_id,
                     # 'loan_type': rec.loan_type_id.name,
                     # 'l_am': round(rec.loan_amount, 2),
                     # 'start_d': rec.start_date,
                     # 'num_terms': rec.term,
                     # 'pa_amount': round(rec.paid_amount, 2),
                     # 'rema_amount': round(rec.remaing_amount, 2),
                     # 'install_amount': round(rec.installment_amount, 2),
                     # 'state_loann': rec.state,
                 })
             www = {
                 'doc_ids': data['ids'],
                 'doc_model': data['model'],
                 'date_from': data['form']['date_from'],
                 'date_to': data['form']['date_to'],
                 'docs': docs,
             }
             print('www#=', www)
             return {
                 'doc_ids': data['ids'],
                 'doc_model': data['model'],
                 'date_from': data['form']['date_from'],
                 'date_to': data['form']['date_to'],
                 'docs': docs,
             }






