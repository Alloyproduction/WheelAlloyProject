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
#     car_type_id = fields.Many2one(comodel_name="vehicle" "Car Make")
    crm_stage = fields.Many2many('crm.stage', string="Stage")
    report_call_reason = fields.Many2one('crm.call.reason', string="Call Reason", track_visibility='onchange')
    report_crm_source_id = fields.Many2one(comodel_name="sale.order.source", string="source", )
    report_city_id = fields.Many2one('res.city', 'Location')


    @api.depends('date_from', 'date_to')
    def see_d(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                    raise ValidationError(" Date To must be bigger than or Equal Date From ")

    @api.multi
    def get_crm_report(self):
        print("get loan"*5)
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




    #print("selff"*5)
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
#                 'car_model_id': str(self.report_city_id.name),
                'crm_stage': str(self.crm_stage.name),
                'report_call_reason': str(self.report_call_reason.name),
                'report_crm_source_id': str(self.report_crm_source_id.name),
                'report_city_id': str(self.report_city_id.name),
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
                # 'stage_id': i.stage_id,
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
         _name = "report.alloy_crm_modification.crm_report_pdf_templ"
         _description = "CRM PDF Report"

         @api.model
         def _get_report_values(self, docids, data=None):


             docs = []
             domains = []

             if data['form']['date_from'] and data['form']['date_to']:
               # print('d==', data['form']['date_from'], data['form']['date_to'])
                domains.append(('create_date', '>=', data['form']['date_from']))
                domains.append(('create_date', '<=', data['form']['date_to']))
             if data['form']['date_from'] and not data['form']['date_to']:
                domains.append(('create_date', '>=', data['form']['date_from']))
             if data['form']['date_to'] and not data['form']['date_from']:
                domains.append(('create_date', '<=', data['form']['date_to']))
             if data['form']['date_to'] and not data['form']['date_from']:
                domains.append(('create_date', '<=', data['form']['date_to']))


             #
             #
             #if str(['form']['crm_stage'][0])=='False':


             #   domains.append(('stage_id', 'in', data['form']['crm_stage']))
             #
#              if str(data['form']['car_model_id'])!='False':
#                 domains.append(('car_type_id', 'in', data['form']['car_model_id']))

             if str(data['form']['report_call_reason'])!='False':
                 domains.append(('call_reason', 'in', data['form']['report_call_reason']))

             if str(data['form']['report_crm_source_id'])!='False':
                 domains.append(('crm_source_id', 'in', data['form']['report_crm_source_id']))


             # if str(data['form']['report_city_id'])!='False':
             #     domains.append(('city_id', 'in', data['form']['report_city_id']))

             if str(data['form']['crm_stage'])!='False':
                 domains.append(('stage_id', 'in', data['form']['crm_stage']))




             crm_report = self.env['crm.lead'].search(domains, order='create_date asc')




             for rec in crm_report:
                 docs.append({
                     'date': rec.create_date,
                     'name': rec.partner_id.name,
                     'car_type': rec.car_type_id.name,
                     'phone': rec.mobile,
                     'location': rec.city_id.name,
                     'inquiry': rec.call_reason.name,
                     'source': rec.crm_source_id.name,
                     'stage': rec.stage_id.name,
                 })
             www = {
                 'doc_model': data['model'],
                 'date_from': data['form']['date_from'],
                 'date_to': data['form']['date_to'],
#                  'car_model_id': data['form']['car_model_id'],
                 'crm_stage': data['form']['crm_stage'],
                 'report_call_reason': data['form']['report_call_reason'],
                 'report_crm_source_id': data['form']['report_crm_source_id'],
                 'report_city_id': data['form']['report_city_id'],
                 'docs': docs,
             }

             return {
                 'doc_ids': data['ids'],
                 'doc_model': data['model'],
                 'date_from': data['form']['date_from'],
                 'date_to': data['form']['date_to'],
#                  'car_model_id': data['form']['car_model_id'],
                 'crm_stage': data['form']['crm_stage'],
                 'report_call_reason': data['form']['report_call_reason'],
                 'report_crm_source_id': data['form']['report_crm_source_id'],
                 'report_city_id': data['form']['report_city_id'],
                 'docs': docs,
             }
