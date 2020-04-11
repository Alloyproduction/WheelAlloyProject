
from odoo import api, fields, models, _ , SUPERUSER_ID
from odoo.addons import decimal_precision as dp

class Picking(models.Model):

    _inherit = "stock.move"

    cost_move =fields.Float( 'Cost' ,store=True )

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





