from odoo import models, fields, api


class StockMovesReportWizard(models.TransientModel):
    _name = 'stockmove.report.wizard'

    prod_categ = fields.Many2many('product.category',string="Category")
    move_location = fields.Many2many('stock.location',string="Location")
    date_from = fields.Date("Date From")
    date_to = fields.Date("Date to")

    @api.multi
    def get_stockmove_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'prod_categ': self.prod_categ.ids,
                'move_location': self.move_location.ids,
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }
        return self.env.ref('ms_report_stock.stockmove_report_report').report_action(self, data=data)


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
            domains.append(('location_id', 'in', data['form']['move_location']))

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

        for sm in stockmove:
            # guarantee_type = dict(sm._fields['guarantee_type'].selection).get(sm.guarantee_type)
            docs.append({
                'date': sm.date,
                'prod_name': sm.product_id.name,
                'consumed_qty': sm.product_uom_qty,
                'previous_qty': sm.old_qty_move,
                'inhand_qty': sm.new_qty_move,
                'rate': round(sm.product_id.standard_price,3),
                'amount': round(sm.product_uom_qty * sm.product_id.standard_price,3),
                'source_request': sm.source_request_move.name,
                'requested_by': sm.employee_user_id_move.name,
                'manage_by': sm.manager_by_move.name,
                'state': sm.state,
            })

        # prod_categ = dict(data['form']._fields['prod_categ'].selection).get(data['form']['prod_categ'])

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'prod_categ': data['form']['prod_categ'],
            'move_location': data['form']['move_location'],
            'date_from': data['form']['date_from'],
            'date_to': data['form']['date_to'],
            'docs': docs,
        }
