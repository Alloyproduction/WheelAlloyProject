from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ReportForGosicustom(models.TransientModel):
    _name = "report.gosi.c"

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date to')
    employee_gosi = fields.Many2one('hr.employee')

    # code_test = fields.Char(string="code_test", default='Gosi', readonly=True)

    # @api.depends('specific_employee', 'specific_date')
    @api.onchange('specific_date')
    def computeTorFff(self):
        for rec in self:
            if rec.specific_date == True:
                rec.specific_employee = False
                rec.employee_gosi = False
#
    @api.onchange('specific_employee')
    def computeTorF(self):
        for rec in self:
            if rec.specific_employee == True:
                rec.specific_date = False
                rec.date_from = False
                rec.date_to = False
#
    specific_employee = fields.Boolean(string="Specific Employee", default=False, store=True)
    specific_date = fields.Boolean(string="Specific Date", default=True, store=True)
#
    @api.depends('date_from', 'date_to')
    def see_d(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                    raise ValidationError(" Date To must be bigger than or Equal Date From ")
#
    @api.multi
    def get_gosi_report(self):
        self.sudo().see_d()
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'employee_gosi': self.employee_gosi.id,
                # 'code_test': self.code_test,
            },
        }
        print('data==', data)
        return self.env.ref('saudi_gosi.gosi_report').report_action(self, data=data)


class GosiReportView(models.AbstractModel):
    _name = "report.saudi_gosi.gosi_report_view"
    _description = "Gosi Report"


    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     payslips = self.env['hr.payslip'].browse(docids)
    #     return {
    #         'doc_ids': docids,
    #         'doc_model': 'hr.payslip',
    #         'docs': payslips,
    #         'data': data,
    #         'get_details_by_rule_category': self.get_details_by_rule_category(
    #             payslips.mapped('details_by_salary_rule_category').filtered(lambda r: r.appears_on_payslip)),
    #         'get_lines_by_contribution_register': self.get_lines_by_contribution_register(
    #             payslips.mapped('line_ids').filtered(lambda r: r.appears_on_payslip)),
    #     }

    @api.model
    def _get_report_values(self, docids, data=None):
        # print("values"*5)
        docs = []
        domains = []
        if data['form']['employee_gosi']:
            # print('employee_gosi id==', data['form']['employee_gosi'])
            ourgosi_id = self.env['hr.payslip'].search([('employee_id', '=', data['form']['employee_gosi'])])
            # print('MM=', ourgosi_id)
            # search in all payslip that has gosi in salary computation
            has_gosi_code = self.env['hr.payslip'].search([])
            # print('has_gosi_code==', has_gosi_code, 'leen==', len(has_gosi_code))
            mylist_with_code = []
            for l in has_gosi_code:
                for e in l.line_ids:
                    if e.code == "GOSI":
                        mylist_with_code.append(l.id)
                        # print(e.code, e.amount)
            # print("mylist_with_code", mylist_with_code)
            the_last_ids = list(set(mylist_with_code).intersection(ourgosi_id.ids))
            # print('the lassst', the_last_ids)
            last_ids = self.env['hr.payslip'].search([('id', 'in', the_last_ids)], order='date_to desc')
            # print('last_ids=====', last_ids)
            # sum total amount in state draft and done
            sum_amount_draft = 0
            sum_amount_done = 0
            sum_amount_draft_for_net_only = 0
            sum_amount_done_for_net_only = 0
            for l in last_ids:
                for m in l.line_ids:
                    # gosi draft or done
                    if m.code == 'GOSI' and l.state == 'draft':
                        sum_amount_draft += m.amount
                        # print('sum_amount_draft000===', sum_amount_draft)
                    if m.code == 'GOSI' and l.state == 'done':
                        sum_amount_done += m.amount
                        # print('sum_amount_draft000===', sum_amount_done)
                    # NET draft or done
                    if m.code == 'NET' and l.state == 'draft':
                        sum_amount_draft_for_net_only += m.amount
                        # print('sum_amount_draft_for_net_only===', sum_amount_draft_for_net_only)
                    if m.code == 'NET' and l.state == 'done':
                        sum_amount_done_for_net_only += m.amount
                        # print('sum_amount_done_for_net_only===', sum_amount_done_for_net_only)
            # sum Gosi draft or done
            # print('sum_amount_draft000===', sum_amount_done)
            total_amount_for_only_done = sum_amount_done
            # print('sum_amount_draft4444===', sum_amount_draft)
            total_amount_for_only_draft = sum_amount_draft
            # sum NET draft or done
            total_amount_for_net_only_draft = sum_amount_draft_for_net_only
            total_amount_for_net_only_only = sum_amount_done_for_net_only
            for rec in last_ids:
                mycode = ''
                myamount = ''
                code_net = ''
                amount_net = ''
                for r in rec.line_ids:
                    if r.code == 'GOSI':
                        mycode = r.code
                        myamount = r.amount
                    if r.code == 'NET':
                        code_net = r.code
                        amount_net = r.amount
                docs.append({
                    'date_from': rec.date_from,
                    'date_to': rec.date_to,
                    'reference': rec.number,
                    'employee_name': rec.employee_id.name,
                    'payslip_name': rec.name,
                    'state': rec.state,
                    'code': mycode,
                    'amount': myamount,
                    'code_for_net': code_net,
                    'amount_for_net': amount_net,
                    'total_amount_for_only_draft': total_amount_for_only_draft,
                    'total_amount_for_only_done': total_amount_for_only_done,
                    'total_amount_for_net_only_draft': total_amount_for_net_only_draft,
                    'total_amount_for_net_only_only': total_amount_for_net_only_only,
                })
            return_onee = {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'date_from': data['form']['date_from'],
                'date_to': data['form']['date_to'],
                'docs': docs,
            }
            return return_onee
        if data['form']['date_from'] or data['form']['date_to']:
            if data['form']['date_from'] and data['form']['date_to']:
                # print('d===', data['form']['date_from'], data['form']['date_to'])
                domains.append(('date_to', '>=', data['form']['date_from']))
                domains.append(('date_to', '<=', data['form']['date_to']))
            if data['form']['date_from'] and not data['form']['date_to']:
                domains.append(('date_to', '>=', data['form']['date_from']))
            if data['form']['date_to'] and not data['form']['date_from']:
                domains.append(('date_to', '<=', data['form']['date_to']))
            print('domain==', domains)
            our_gosi = self.env['hr.payslip'].search([('state', 'in', ['draft', 'done'])] and domains, order='date_to desc')
            print('ourgosi=', our_gosi, 'leen=', len(our_gosi)), print('our==', our_gosi.ids, 'leen=', len(our_gosi.ids))
            # search in all payslip that has gosi in salary computation
            has_gosi_code = self.env['hr.payslip'].search([])
            # print('has_gosi_code==', has_gosi_code, 'leen==', len(has_gosi_code))
            mylist_with_code = []
            for l in has_gosi_code:
                for e in l.line_ids:
                    if e.code == "GOSI":
                        mylist_with_code.append(l.id)
                        # print(e.code, e.amount)
            # print("mylist_with_code", mylist_with_code)
            the_last_ids = list(set(mylist_with_code).intersection(our_gosi.ids))
            # print('the lassst', the_last_ids)
            last_ids = self.env['hr.payslip'].search([('id', 'in', the_last_ids)], order='date_to desc')
            print('last_ids=====', last_ids)
            # sum total amount in state draft and done
            sum_amount_draft = 0
            sum_amount_done = 0
            sum_amount_draft_for_net_only = 0
            sum_amount_done_for_net_only = 0
            for l in last_ids:
                for m in l.line_ids:
                    # gosi draft or done
                    if m.code == 'GOSI' and l.state == 'draft':
                        sum_amount_draft += m.amount
                        print('sum_amount_draft000===', sum_amount_draft)
                    if m.code == 'GOSI' and l.state == 'done':
                        sum_amount_done += m.amount
                        print('sum_amount_draft000===', sum_amount_done)
                    # NET draft or done
                    if m.code == 'NET' and l.state == 'draft':
                        sum_amount_draft_for_net_only += m.amount
                        print('sum_amount_draft_for_net_only===', sum_amount_draft_for_net_only)
                    if m.code == 'NET' and l.state == 'done':
                        sum_amount_done_for_net_only += m.amount
                        print('sum_amount_done_for_net_only===', sum_amount_done_for_net_only)
            # sum Gosi draft or done
            print('sum_amount_draft000===', sum_amount_done)
            total_amount_for_only_done = sum_amount_done
            print('sum_amount_draft4444===', sum_amount_draft)
            total_amount_for_only_draft = sum_amount_draft
            # sum NET draft or done
            total_amount_for_net_only_draft = sum_amount_draft_for_net_only
            total_amount_for_net_only_only = sum_amount_done_for_net_only
            for rec in last_ids:
                mycode = ''
                myamount = ''
                code_net = ''
                amount_net = ''
                for r in rec.line_ids:
                    if r.code == 'GOSI':
                        mycode = r.code
                        myamount = r.amount
                    if r.code == 'NET':
                        code_net = r.code
                        amount_net = r.amount
                docs.append({
                    'date_from': rec.date_from,
                    'date_to': rec.date_to,
                    'reference': rec.number,
                    'employee_name': rec.employee_id.name,
                    'payslip_name': rec.name,
                    'state': rec.state,
                    'code': mycode,
                    'amount': myamount,
                    'code_for_net': code_net,
                    'amount_for_net': amount_net,
                    'total_amount_for_only_draft': total_amount_for_only_draft,
                    'total_amount_for_only_done': total_amount_for_only_done,
                    'total_amount_for_net_only_draft': total_amount_for_net_only_draft,
                    'total_amount_for_net_only_only': total_amount_for_net_only_only,
                })
            return_one = {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'date_from': data['form']['date_from'],
                    'date_to': data['form']['date_to'],
                    'docs': docs,
            }
            # print('return_one#=', return_one)
            return return_one
