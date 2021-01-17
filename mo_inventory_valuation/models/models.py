# -*- coding: utf-8 -*-


from odoo import api, models, fields, _



class StockQuantityHistory(models.TransientModel):
    _inherit = 'stock.quantity.history'

    prod_categ_ids = fields.Many2many('product.category', 'mo_report2_stock_categ_rel', 'mo_report_stock_id',
        'categ_id', 'Categories')
    stock_loc_ids = fields.Many2many('stock.location', 'mo_report2_stock_location_rel', 'mo_report_stock_id',
        'location_id', 'Locations')


    def open_table(self):
        self.ensure_one()

        if self.compute_at_date:
            print('OKKK')
            tree_view_id = self.env.ref('stock_account.view_stock_product_tree2').id
            form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
            # We pass `to_date` in the context so that `qty_available` will be computed across
            # moves until date.

            if self.stock_loc_ids and not self.prod_categ_ids:
                domain = [('type', '=', 'product'),('stock_quant_ids.location_id', 'in', self.stock_loc_ids.ids)]
                print('Cond01')

            elif self.prod_categ_ids and not self.stock_loc_ids:
                domain = [('type', '=', 'product'),('categ_id', 'in', self.prod_categ_ids.ids)]
                print('Cond02')

            elif self.prod_categ_ids and self.stock_loc_ids:
                domain = [('type', '=', 'product'),('categ_id', 'in', self.prod_categ_ids.ids),
                          ('stock_quant_ids.location_id', 'in', self.stock_loc_ids.ids)]
                print('Cond03')

            else:
                domain = [('type', '=', 'product')]
                print('Cond04')

            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Products'),
                'res_model': 'product.product',
                'domain': domain,
                'context': dict(self.env.context, to_date=self.date),
            }
            return action

        else:
            print('else worked')
            self.env['stock.quant']._merge_quants()
            self.env['stock.quant']._unlink_zero_quants()


            if self.stock_loc_ids and not self.prod_categ_ids:
                x = self.env.ref('stock.quantsact').read()[0]
                x['domain'] = [('product_id.type', '=', 'product'),('location_id', 'in', self.stock_loc_ids.ids)]
                print('011')
            elif self.prod_categ_ids and not self.stock_loc_ids:
                x = self.env.ref('stock.quantsact').read()[0]
                x['domain'] = [('product_id.type', '=', 'product'),('product_id.categ_id', 'in', self.prod_categ_ids.ids)]
                print('022')

            elif self.stock_loc_ids and self.prod_categ_ids:
                x = self.env.ref('stock.quantsact').read()[0]
                x['domain'] = [('product_id.type', '=', 'product'),('location_id', 'in', self.stock_loc_ids.ids),
                               ('product_id.categ_id', 'in', self.prod_categ_ids.ids)]
                print('033')
            else:
                x = self.env.ref('stock_account.product_valuation_action').read()[0]
                print('044')

            print(x)
            print('success test')
            return x
