
from odoo import api, fields, models, _ , SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round, float_is_zero


# class StockMoveLineTechnician(models.Model):
#     _inherit = "benefit.request.line"
#
#     employee_user_id_move_line = fields.Many2one('res.users',
#                                                  'Requester Name', store=True,
#
#                                                  track_visibility='onchange',
#                                                  )
class Picking(models.Model):

    _inherit = "stock.move"

    cost_move =fields.Float( 'Amount Cost' ,store=True )

    old_qty_move = fields.Float(string='Old Quantity', track_visibility='onchange',
                                   digits=dp.get_precision('Product Unit of Measure') ,store=True )
    new_qty_move = fields.Float(string='new Quantity', track_visibility='onchange',
                                   digits=dp.get_precision('Product Unit of Measure'),store=True)
    amount_qty_move = fields.Float(string='amount', track_visibility='onchange',
                                      digits=dp.get_precision('Product Unit of Measure'),store=True)

    source_request_move = fields.Many2one('tech.request',
                                     'Source Request',

                                     track_visibility='onchange', store=True
                                      )

    employee_user_id_move = fields.Many2one('res.users',
                                       'Employee Request',store=True,

                                       track_visibility='onchange',
                                       )
    manager_by_move = fields.Many2one('res.users',
                                 'Manage by',

                                 track_visibility='onchange',store=True
                                  )
    
    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        self.ensure_one()
        # apply putaway
        location_dest_id = self.location_dest_id.get_putaway_strategy(self.product_id).id or self.location_dest_id.id

        vals = {
            'move_id': self.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': location_dest_id,
            'picking_id': self.picking_id.id,
         }
        if self.employee_user_id_move :
            vals = {
                'move_id': self.id,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom.id,
                'location_id': self.location_id.id,
                'location_dest_id': location_dest_id,
                'picking_id': self.picking_id.id,
                'employee_user_id_move_line': self.employee_user_id_move.id,
            }
        if quantity:
            uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom,
                                                                    rounding_method='HALF-UP')
            uom_quantity_back_to_product_uom = self.product_uom._compute_quantity(uom_quantity, self.product_id.uom_id,
                                                                                  rounding_method='HALF-UP')
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                vals = dict(vals, product_uom_qty=uom_quantity)
            else:
                vals = dict(vals, product_uom_qty=quantity, product_uom_id=self.product_id.uom_id.id)
        if reserved_quant:
            vals = dict(
                vals,
                location_id=reserved_quant.location_id.id,
                lot_id=reserved_quant.lot_id.id or False,
                package_id=reserved_quant.package_id.id or False,
                owner_id=reserved_quant.owner_id.id or False,
            )
        return vals







