# -*- coding: utf-8 -*-


from odoo import models, fields, api, _

from odoo.tools.misc import formatLang, format_date, get_user_companies

from odoo.tools.translate import _
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError

class PartnerDueXlsx(models.AbstractModel):
    _name = 'report.account_due_excel.report_due_xlsx'

    _inherit =  'report.report_xlsx.abstract'


    def _get_columns_name(self, options):
        """
        Override
        Return the name of the columns of the follow-ups report
        """
        headers = [{},
                   {'name': _('Date'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Due Date'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Source Document'), 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Communication'), 'style': 'text-align:right; white-space:nowrap;'},
                   {'name': _('Expected Date'), 'class': 'date', 'style': 'white-space:nowrap;'},
                   {'name': _('Excluded'), 'class': 'date', 'style': 'white-space:nowrap;'},
                   {'name': _('Total Due'), 'class': 'number o_price_total',
                    'style': 'text-align:right; white-space:nowrap;'}
                   ]
        if self.env.context.get('print_mode'):
            headers = headers[:5] + headers[7:]  # Remove the 'Expected Date' and 'Excluded' columns
        return headers

    def _get_lines(self, options, line_id=None):
        """
        Override
        Compute and return the lines of the columns of the follow-ups report.
        """
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []
        lang_code = partner.lang or self.env.user.lang or 'en_US'

        lines = []
        res = {}
        today = fields.Date.today()
        line_num = 0
        for l in partner.unreconciled_aml_ids.filtered(lambda l: l.company_id == self.env.user.company_id):
            if l.company_id == self.env.user.company_id:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            for aml in aml_recs:
                amount = aml.currency_id and aml.amount_residual_currency or aml.amount_residual
                date_due = format_date(self.env, aml.date_maturity or aml.date, lang_code=lang_code)
                total += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date',
                                'style': 'white-space:nowrap;text-align:center;color: red;'}
                if is_payment:
                    date_due = ''
                move_line_name = aml.invoice_id.name or aml.name
                if self.env.context.get('print_mode'):
                    move_line_name = {'name': move_line_name, 'style': 'text-align:right; white-space:normal;'}
                amount = formatLang(self.env, amount, currency_obj=currency)
                line_num += 1
                expected_pay_date = format_date(self.env, aml.expected_pay_date,
                                                lang_code=lang_code) if aml.expected_pay_date else ''
                columns = [
                    format_date(self.env, aml.date, lang_code=lang_code),
                    date_due,
                    aml.invoice_id.origin,
                    move_line_name,
                    expected_pay_date + ' ' + (aml.internal_note or ''),
                    {'name': aml.blocked, 'blocked': aml.blocked},
                    amount,
                ]
                if self.env.context.get('print_mode'):
                    columns = columns[:4] + columns[6:]
                lines.append({
                    'id': aml.id,
                    'invoice_id': aml.invoice_id.id,
                    'view_invoice_id': self.env['ir.model.data'].get_object_reference('account', 'invoice_form')[1],
                    'account_move': aml.move_id,
                    'name': aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'has_invoice': bool(aml.invoice_id),
                    'columns': [type(v) == dict and v or {'name': v} for v in columns],
                })
            total_due = formatLang(self.env, total, currency_obj=currency)
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total',
                'unfoldable': False,
                'level': 0,
                'columns': [{'name': v} for v in [''] * (3 if self.env.context.get('print_mode') else 5) + [
                    total >= 0 and _('Total Due') or '', total_due]],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued, currency_obj=currency)
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'unfoldable': False,
                    'level': 0,
                    'columns': [{'name': v} for v in
                                [''] * (3 if self.env.context.get('print_mode') else 5) + [_('Total Overdue'),
                                                                                           total_issued]],
                })
            # Add an empty line after the total to make a space between two currencies
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': '',
                'unfoldable': False,
                'level': 0,
                'columns': [{} for col in columns],
            })
        # Remove the last empty line
        if lines:
            lines.pop()
        return lines

    def generate_xlsx_report(self, workbook, data, partners):

        red_mark = workbook.add_format({'font_size': 12, 'font_color': 'red'})
        normal_size = workbook.add_format({'font_size': 16  ,  'text_wrap': True})
        normal = workbook.add_format({'bold': False})
        options={}
        for obj in partners:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, obj.name, bold)
            options['partner_id']=obj.id
            print(self._get_columns_name(options))
            dic =self._get_columns_name(options)
            i=2
            j=0;
            sheet.write(i, j, ' ', bold)
            j=1
            for col in dic :
                if col :
                    # print(col['name'])
                    sheet.write(i, j, col['name'], bold)
                    j +=1

            # print(self._get_lines(options))
#             str ="Dear Sir/Madam, \
# Our records indicate that some payments on your account are still due. Please find details below. \
# If the amount has already been paid, please disregard this notice. Otherwise, please forward us the total amount stated below.\
# If you have any queries regarding your account, Please contact us.\
# Thank you in advance for your cooperation.\
# Best Regards,"
#             sheet.write(2,1, str, normal_size)
            dic_lines = self._get_lines(options)
            i = 3
            j = 0;
            for col_lines in dic_lines:
                j = 0
                sheet.write(i, j, col_lines['name'], normal)
                j = 1
                for list in col_lines['columns']:


                  if len(list) >2:
                    sheet.write(i, j, list['name'],red_mark)
                  else:
                    sheet.write(i, j, list['name'], normal)
                  j+=1
                i+=1
                    #     sheet.write(i, j, list['name'],normal)
                        # sheet.write(i, j, obj['name'], bold)
                        # j += 1
                        # for list in obj['columns']:
                        #     print(list['name'])
                        #     sheet.write(i, j, list['name'],normal)
                        #     j += 1
                        # i += 1

class myduepartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def print_quotation_xls(self):
        return self.env.ref('account_due_excel.partner_Due_xlsx').report_action(self)

#
# class account_due_excel(models.Model):
#     _name = 'report.account_due_excel.report_due_xlsx'
#     _inherit  = 'account.followup.report'
#
#     @api.model
#     def print_followups(self, records):
#         """
#         Print one or more followups in one PDF
#         records contains either a list of records (come from an server.action) or a field 'ids' which contains a list of one id (come from JS)
#         """
#         res_ids = records['ids'] if 'ids' in records else records.ids  # records come from either JS or server.action
#         self.env['res.partner'].browse(res_ids).message_post(body=_('Follow-up letter printed'))

#         return self.env.ref('account_reports.action_report_followup').report_action(res_ids)
#
# #     name = fields.Char()
# #     value = fields.Integer()
# #     value2 = fields.Float(compute="_value_pc", store=True)
# #     description = fields.Text()
# #
# #     @api.depends('value')
# #     def _value_pc(self):
# #         self.value2 = float(self.value) / 100