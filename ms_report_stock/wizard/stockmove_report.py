from odoo import models, fields, api

from datetime import datetime
from datetime import timedelta
import itertools
from operator import itemgetter
import operator
# ========For Excel========
from io import BytesIO
import xlwt
from xlwt import easyxf
import base64


class StockMovesReportWizard(models.TransientModel):
    _name = 'stockmove.report.wizard'

    prod_categ = fields.Many2many('product.category', string="Category")
    move_location = fields.Many2many('stock.location', relation="stock_move_loc22",column1="ha1", column2="ha2",
                                     string="Source Location",store=True)
    move_location_dest = fields.Many2many('stock.location', relation="stock_move_loc88",column1="ha33", column2="ha55",
                                     string="Source Location",store=True)
    date_from = fields.Date("Date From")
    date_to = fields.Date("Date to")
# _________________________________________________
    excel_file = fields.Binary('Excel File')

# ____________________________________

    @api.multi
    def get_stockmove_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'prod_categ': self.prod_categ.ids,
                'move_location': self.move_location.ids,
                'move_location_dest': self.move_location_dest.ids,
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }
        print('data', data)
        return self.env.ref('ms_report_stock.stockmove_report_report').report_action(self, data=data)

# _____________________________________________________________________________________________________

    def get_product_ids(self):
        product_pool = self.env['product.product']
        if self.filter_by and self.filter_by == 'product':
            return self.product_ids.ids
        else:
            product_ids = product_pool.search([('type', '=', 'product')])
            return product_ids.ids

    def get_lines(self):
        product_ids = self.get_product_ids()
        result = []
        if product_ids:
            in_lines = self.in_lines(product_ids)
            out_lines = self.out_lines(product_ids)
            lst = in_lines + out_lines
            new_lst = sorted(lst, key=itemgetter('product'))
            groups = itertools.groupby(new_lst, key=operator.itemgetter('product'))
            result = [{'product': k, 'values': [x for x in v]} for k, v in groups]
            for res in result:
                print
                l_data = res.get('values')
                new_lst = sorted(l_data, key=itemgetter('date'))
                print("")
                res['values'] = new_lst
        return result
        product_ids = self.get_product_ids()
        result = []
        return result

    def get_style(self):
        main_header_style = easyxf('font:height 300;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")
        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz right;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")
        left_header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                                   'align: horiz left;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")
        text_left = easyxf('font:height 200; align: horiz left;')
        text_right = easyxf('font:height 200; align: horiz right;', num_format_str='0.00')
        text_left_bold = easyxf('font:height 200; align: horiz right;font:bold True;')
        text_right_bold = easyxf('font:height 200; align: horiz right;font:bold True;', num_format_str='0.00')
        text_center = easyxf('font:height 200; align: horiz center;'
                             "borders: top thin,left thin,right thin,bottom thin")

        group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
                             'align: horiz left;font: color black; font:bold True;'
                             "borders: top thin,left thin,right thin,bottom thin")
        return [main_header_style, left_header_style, header_style, text_left, text_right, text_left_bold,
                text_right_bold, text_center, group_style]

    @api.model
    def _get_data(self):
        docs = []
        domains = []
        if self.prod_categ:
            domains.append(('product_id.categ_id', 'in', self.prod_categ.ids))

        if self.move_location:
            print('LLLLLLLLL', self.move_location.name)
            domains.append(('location_id', 'in', self.move_location.ids))

        if self.move_location_dest:
            print('LLL222', self.move_location_dest.name)
            print("there are move_location_dest")
            domains.append(('location_dest_id', 'in', self.move_location_dest.ids))

        if self.date_from and self.date_to:
            domains.append(('date', '>=', self.date_from))
            domains.append(('date', '<=', self.date_to))
        if self.date_from and not self.date_to:
            domains.append(('date', '>=', self.date_from))
        if self.date_from and not self.date_to:
            domains.append(('date', '<=', self.date_to))

        print('DDDDDDDD',domains)
        stockmove = self.env['stock.move'].search(domains, order='reference asc')
        # else:
        #     print('else')
        #     stockmove = self.env['stock.move'].search([], order='name asc')
        print('stockmove', stockmove)
        # print(data['form']['prod_categ'])
        # print(data['form']['move_location'])
        for sm in stockmove:
            # guarantee_type = dict(sm._fields['guarantee_type'].selection).get(sm.guarantee_type)
            docs.append({
                'date': sm.date,
                'reference': sm.reference,
                'prod_name': sm.product_id.name,
                'consumed_qty': sm.product_uom_qty,
                'previous_qty': sm.old_qty_move,
                'inhand_qty': sm.new_qty_move,
                'rate': round(sm.product_id.standard_price, 3),
                # 'amount': round(sm.product_uom_qty * sm.product_id.standard_price, 3),
                'amount': sm.amount_qty_move,
                'source_request': sm.source_request_move.name,
                'requested_by': sm.employee_user_id_move.name,
                'manage_by': sm.manager_by_move.name,
                'state': sm.state,
            })
        return {
            'doc_ids': self.ids,
            # 'doc_model': self.model,
            'prod_categ': self.prod_categ,
            'move_location': self.move_location,
            'move_location_dest': self.move_location_dest,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'docs': docs,
        }

    def create_excel_header(self, worksheet, main_header_style, text_left, text_center, left_header_style, text_right,
                            header_style):
        worksheet.write_merge(0, 1, 1, 3, 'Cost of Goods Sold Report', main_header_style)
        row = 2
        col = 1
        date_from = datetime.strptime(str(self.date_from), '%Y-%m-%d')
        date_from = datetime.strftime(date_from, "%d-%m-%Y ")
        date_to = datetime.strptime(str(self.date_to), '%Y-%m-%d')
        date_to = datetime.strftime(date_to, "%d-%m-%Y ")
        date = 'Date From: '+ date_from + ' Date To: ' + date_to
        worksheet.write_merge(row, row, col, col + 2, date, text_center)
        row += 2
        row += 2
        worksheet.write(row, 0, '#', left_header_style)
        worksheet.write(row, 1, 'Date', left_header_style)
        worksheet.write(row, 2, 'Reference', left_header_style)
        worksheet.write(row, 3, 'Product', left_header_style)
        worksheet.write(row, 4, 'Consumed Qty', left_header_style)
        worksheet.write(row, 5, 'Previous Qty', left_header_style)
        worksheet.write(row, 6, 'In Hand Qty', left_header_style)
        worksheet.write(row, 7, 'Rate', left_header_style)
        worksheet.write(row, 8, 'Amount', left_header_style)
        worksheet.write(row, 9, 'Source Request', left_header_style)
        worksheet.write(row, 10, 'Requested By', left_header_style)
        worksheet.write(row, 11, 'Manage By', left_header_style)
        worksheet.write(row, 12, 'Status', left_header_style)
        lines = self._get_data()
        print('all lines', lines)
        docs = lines['docs']
        # lines = self.env['product.product']
        p_group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ivory;'
                               'align: horiz left;font: color black; font:bold True;'
                               "borders: top thin,left thin,right thin,bottom thin")
        group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
                             'align: horiz left;font: color black; font:bold True;'
                             "borders: top thin,left thin,right thin,bottom thin")
        group_style_right = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
                                   'align: horiz right;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin", num_format_str='0.00')

        text_left = easyxf('font:height 200; align: horiz left;')
        row += 1
        seq = 0
        sum_consumed_qty = 0
        sum_previous_qty = 0
        sum_inhand_qty = 0
        sum_rate = 0
        sum_amount = 0
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd/mm/yyyy'
        for line in docs:
            print("date", line['date'])
            print("reference", line['reference'])
            print("stateeeee", line['state'])
            # if line['state'] == 'cancel':
            #     print('ccccccccccc') #17
            #     pass
            # else:
            if line['state'] == 'done':
                print('ddddddddddd') #125
                seq += 1
                # if seq == 1:
                worksheet.write(row, 0, seq, text_left)
                worksheet.write(row, 1, line['date'], date_format)
                worksheet.write(row, 2, line['reference'], text_left)
                worksheet.write(row, 3, line['prod_name'], text_left)
                worksheet.write(row, 4, line['consumed_qty'], text_right)
                worksheet.write(row, 5, line['previous_qty'], text_right)
                worksheet.write(row, 6, line['inhand_qty'], text_right)
                worksheet.write(row, 7, line['rate'], text_right)
                worksheet.write(row, 8, line['amount'], text_right)
                worksheet.write(row, 9, line['source_request'], text_right)
                worksheet.write(row, 10, line['requested_by'], text_right)
                worksheet.write(row, 11, line['manage_by'], text_right)
                worksheet.write(row, 12, line['state'], text_right)
                row += 1
                sum_consumed_qty += line['consumed_qty']
                sum_previous_qty += line['previous_qty']
                sum_inhand_qty += line['inhand_qty']
                sum_rate += line['rate']
                sum_amount += line['amount']
            else:
                print('ssssssssssss') #125
                pass
        worksheet.write(row, 4, sum_consumed_qty, group_style)
        worksheet.write(row, 5, sum_previous_qty, group_style)
        worksheet.write(row, 6, sum_inhand_qty, group_style)
        worksheet.write(row, 7, sum_rate, group_style)
        worksheet.write(row, 8, sum_amount, group_style)
        row += 1
        return worksheet, row


    def get_excel(self):
        # Style of Excel Sheet
        excel_style = self.get_style()
        main_header_style = excel_style[0]
        left_header_style = excel_style[1]
        header_style = excel_style[2]
        text_left = excel_style[3]
        text_right = excel_style[4]
        text_left_bold = excel_style[5]
        text_right_bold = excel_style[6]
        text_center = excel_style[7]
        # ====================================
        workbook = xlwt.Workbook()
        filename = 'Cost of Goods Sold Report.xls'
        worksheet = workbook.add_sheet('Stock Card', cell_overwrite_ok=True)
        for i in range(0, 10):
            worksheet.col(i).width = 150 * 30

        worksheet, row = self.create_excel_header(worksheet, main_header_style, text_left, text_center,
                                                  left_header_style, text_right, header_style)

        # download Excel File
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        excel_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'excel_file': excel_file})

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=stockmove.report.wizard&download=true&field=excel_file&id=%s&filename=%s' % (
                    active_id, filename),
                'target': 'new',
            }
    # ______________________________________________________________________________________

class StockMovesReportReportView(models.AbstractModel):
    _name = "report.ms_report_stock.stockmove_report_report_view"
    _description = "Stock Moves Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        domains = []
        if data['form']['prod_categ']:
            domains.append(('product_id.categ_id', 'in', data['form']['prod_categ']))
        if data['form']['move_location']:
            print('Location000000', data['form']['move_location'][0])
            # loca_name = data['form']['move_location'][0]
            # all_loca_Source = ['36', '8', '12', '32', '5']
            # if loca_name in all_loca_Source:
            #     print("GGGGGGGGGGGGGGG")
            #     print("there are v location")
            #     domains.append(('location_id', 'in', data['form']['move_location']))
            #     print('LLL after Apend', data['form']['move_location'])
            # else:
            #     print("EEEEEEEEEEE")
            #     domains.append(('location_dest_id', 'in', data['form']['move_location']))
            #     print('Location after Append', data['form']['move_location'])
            domains.append(('location_id', 'in', data['form']['move_location']))

        if data['form']['move_location_dest']:
            domains.append(('location_dest_id', 'in', data['form']['move_location_dest']))

        if data['form']['date_from'] and data['form']['date_to']:
            domains.append(('date', '>=', data['form']['date_from']))
            domains.append(('date', '<=', data['form']['date_to']))
        if data['form']['date_from'] and not data['form']['date_to']:
            domains.append(('date', '>=', data['form']['date_from']))
        if data['form']['date_to'] and not data['form']['date_from']:
            domains.append(('date', '<=', data['form']['date_to']))
        stockmove = self.env['stock.move'].search(domains, order='reference asc')
        # else:
        #     print('else')
        #     stockmove = self.env['stock.move'].search([], order='name asc')

        print('stockmove')
        print(stockmove)

        print(data['form']['prod_categ'])
        print(data['form']['move_location'])
        print(data['form']['move_location_dest'])

        for sm in stockmove:
            # guarantee_type = dict(sm._fields['guarantee_type'].selection).get(sm.guarantee_type)
            docs.append({
                'date': sm.date,
                'reference': sm.reference,
                'prod_name': sm.product_id.name,
                'consumed_qty': sm.product_uom_qty,
                'previous_qty': sm.old_qty_move,
                'inhand_qty': sm.new_qty_move,
                'rate': round(sm.product_id.standard_price,3),
                # 'amount': round(sm.product_uom_qty * sm.product_id.standard_price,3),
                'amount': sm.amount_qty_move,
                'source_request': sm.source_request_move.name,
                'requested_by': sm.employee_user_id_move.name,
                'manage_by': sm.manager_by_move.name,
                'state': sm.state,
            })

        # prod_categ = dict(data['form']._fields['prod_categ'].selection).get(data['form']['prod_categ'])
        mm={
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'prod_categ': data['form']['prod_categ'],
            'move_location': data['form']['move_location'],
            'move_location_dest': data['form']['move_location_dest'],
            'date_from': data['form']['date_from'],
            'date_to': data['form']['date_to'],
            'docs': docs,
        }
        print('MM=', mm)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'prod_categ': data['form']['prod_categ'],
            'move_location': data['form']['move_location'],
            'move_location_dest': data['form']['move_location_dest'],
            'date_from': data['form']['date_from'],
            'date_to': data['form']['date_to'],
            'docs': docs,
        }
