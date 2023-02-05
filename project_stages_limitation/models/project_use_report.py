from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import request
import base64
import io


class ReportForLoan(models.TransientModel):
    _name = "report.project.custom"

    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date to', required=True)
    user = fields.Many2one('res.users', string='User')
    sale = fields.Many2one('sale.order', 'Sales Order')
    task = fields.Many2many('project.task', string="Task", track_visibility='onchange')
    project = fields.Many2one('project.project', string="Project", track_visibility='onchange')



    @api.depends('date_from', 'date_to')
    def see_d(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                    raise ValidationError(" Date To must be bigger than or Equal Date From ")

    @api.multi
    def get_project_report(self):
        print("get loan"*5)
        self.sudo().see_d()
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }

        return self.env.ref('project_stages_limitation.project_report').report_action(self, data=data)



    @api.multi
    def get_project_report_pdf(self):
        self.sudo().see_d()


        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'user': self.user,
                'sale': self.sale,
                'task': str(self.task.name),
                'project': str(self.project.name),
            },
        }
        return self.env.ref('project_stages_limitation.project_report_pdf').report_action(self, data=data)

#########################################################################################################################################

class projectReportViewpdf(models.AbstractModel):
         _name = "report.project_stages_limitation.project_report_pdf_templ"
         _description = "Project PDF Report"

         @api.model
         def _get_report_values(self, docids, data=None):


             docs = []
             domains = []

             if data['form']['date_from'] and data['form']['date_to']:
                domains.append(('create_date', '>=', data['form']['date_from']))
                domains.append(('create_date', '<=', data['form']['date_to']))
             if data['form']['date_from'] and not data['form']['date_to']:
                domains.append(('create_date', '>=', data['form']['date_from']))
             if data['form']['date_to'] and not data['form']['date_from']:
                domains.append(('create_date', '<=', data['form']['date_to']))
             if data['form']['date_to'] and not data['form']['date_from']:
                domains.append(('create_date', '<=', data['form']['date_to']))


             # if str(['form']['user'][0])=='False':
             # if str(data['form']['user']) != 'False':
             #   domains.append(('user_id', 'in', data['form']['user']))

             if str(data['form']['sale']) != 'False':
                 domains.append(('sale_name', 'in', data['form']['sale']))

             if str(data['form']['task']) != 'False':
                 domains.append(('task_number', 'in', data['form']['task']))

             if str(data['form']['project']) != 'False':
                 domains.append(('project_name', 'in', data['form']['project']))

             # if str(data['form']['user']) != 'False':
             #     domains.append(('user_id', 'in', data['form']['user']))

             project_report = self.env['product.task.used'].search(domains, order='create_date asc')


             for rec in project_report:
                 docs.append({
                     'date': rec.create_date,
                     'u_ser': rec.user_id.name,
                     't_ask': rec.task_number.name,
                     'p_roject': rec.project_name.name,
                     's_order': rec.sale_name.name,
                     'product': rec.product_id.name,
                     'quantity': rec.product_qty,
                     'unit': rec.used_unit,
                     'cost': rec.product_cost,
                     'total': rec.total_cost,
                 })
             www = {
                 'doc_model': data['model'],
                 'date_from': data['form']['date_from'],
                 'date_to': data['form']['date_to'],
                 'sale': data['form']['sale'],
                 'user': data['form']['user'],
                 'task': data['form']['task'],
                 'project': data['form']['project'],
                 'docs': docs,
             }

             return {
                 'doc_ids': data['ids'],
                 'doc_model': data['model'],
                 'date_from': data['form']['date_from'],
                 'date_to': data['form']['date_to'],
                 'sale': data['form']['sale'],
                 'user': data['form']['user'],
                 'task': data['form']['task'],
                 'project': data['form']['project'],
                 'docs': docs,
             }
