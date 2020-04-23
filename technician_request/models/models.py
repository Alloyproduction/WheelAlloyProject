
from odoo import api, fields, models, _ , SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


_REQUESTSTATES = [
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('done', 'Done'),
    ('rejected', 'Rejected')
]

class TechicianRequest(models.Model):
    _name = 'tech.request'
    _description = 'Technician Request'
    _inherit = ['mail.thread']

    @api.model
    def _get_Employee_request(self):
        res=self.env['res.users'].browse(self.env.uid)
        return res


    @api.model
    def _get_default_loc_from(self):
        uid = self.env['res.users'].browse(self.env.uid)
        # print("uid.location_from.id",uid.location_from.id)
        return uid.location_from.id


    @api.model
    def _get_default_loc_to(self):
        uid = self.env['res.users'].browse(self.env.uid)
        # print("uid.location_to.id",uid.location_to.id)
        return uid.location_to.id

    @api.model
    def _get_default_op_type(self):
        uid = self.env['res.users'].browse(self.env.uid)
        # print("uid.operation_type.id",uid.operation_type.id)
        return uid.operation_type.id

    @api.multi
    def _get_default_manager_by(self):
        uid=self.env['res.users'].browse(self.env.uid)
        if uid.location_from.manager_ids:
            # print("hi.. ")
            # print(uid.location_from.manager_ids)
            return uid.location_from.manager_ids
        return []

    @api.model
    def _get_default_name_tec(self):
        seq1 = self.env['ir.sequence'].next_by_code('tech.request.name')

        return seq1

    @api.model
    def _get_default_name_code(self):
        seq1=self.env['ir.sequence'].next_by_code('tech.request')
        return seq1


    name = fields.Char('Request Name', size=40, required=True,default = _get_default_name_tec ,track_visibility='onchange')
    Requestcode = fields.Char('Request Code', size=40, required=True, default=_get_default_name_code, track_visibility='onchange')
    start_date = fields.Datetime('Start date',   help="Date of create the request.",   default=datetime.now(),
                             track_visibility='onchange')

    request_by = fields.Many2one('res.users',  'Requested by',required=True,  track_visibility='onchange',
                                   default=_get_Employee_request,readonly=True)

    Location_manager_ids = fields.Many2many('res.users', string='Manager of Location', default=_get_default_manager_by  )
    Location_u_from = fields.Many2one('stock.location', string='Location From', default=_get_default_loc_from)
    Location_u_to = fields.Many2one('stock.location', string='Location To', default=_get_default_loc_to)
    operation_u_type = fields.Many2one('stock.picking.type', string='Operation type', default=_get_default_op_type)

    desc = fields.Text('Description of the Request')

    products_line_ids = fields.One2many('tech.request.line', 'request_line_id',   'Products to Request',
                               copy=True,
                               track_visibility='onchange')

    state = fields.Selection(selection=_REQUESTSTATES,
                             string='Status',
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')

    @api.multi
    @api.onchange('state','name')
    def _compute_manager_ids(self):
        u_id=self.env['res.users'].browse(self.env.uid)
        if u_id.location_from.manager_ids :

            self.Location_manager_ids=u_id.location_from.manager_ids
            # print(u_id.location_from.manager_ids)


    @api.multi
    @api.depends('state')
    def _compute_can_editable(self):
        for rec in self:
            if rec.state in ('sent', 'ready', 'done', 'rejected'):
                rec.can_editable = False
            else:
                rec.can_editable = True

    can_editable = fields.Boolean(string="Can editable",
                                 compute="_compute_can_editable",
                                 readonly=True)


    @api.multi
    def button_to_draft(self):
        self.mapped('products_line_ids').uncancel()
        return self.write({'state': 'draft'})

    @api.multi
    def button_send(self):
        self.send_m('New Technician request Request from '+self.request_by.name,'New Technician request require to be ready')
        return self.write({'state': 'sent'})


    @api.multi
    def button_ready(self):
        self.send_m('The Request('+self.name+') is ready', ''+'The Request('+self.name+') is ready from '+self.request_by.location_from.name )
        return self.write({'state': 'done'})



    @api.multi
    def button_to_rejected(self):
        self.mapped('products_line_ids').cancel()
        self.send_m('The Request('+self.name+') is rejected ', ''+'The Request('+self.name+') is rejected  ' )
        return self.write({'state': 'rejected'})



    def send_m(self, msubj="", mbody=""  ):
        recipient_partners = []
        if self.request_by.partner_id.id and self.request_by.partner_id.id not in recipient_partners:
            recipient_partners.append(self.request_by.partner_id.id)
        if self.Location_manager_ids:
            for m in self.Location_manager_ids:
                if m.partner_id.id not in recipient_partners:
                    recipient_partners.append(m.partner_id.id)




        if msubj != "":
            msgsubject = msubj

        if mbody != "":
            msgbody = mbody

        print(recipient_partners)

        if len(recipient_partners):
            self.message_post(body=msgbody,
                              subtype='mt_comment',
                              subject=msgsubject,
                              partner_ids=recipient_partners,
                              message_type='comment')

    @api.multi
    def make_transfer(self):
        view_id = self.env.ref('stock.view_picking_form')


        products_order_line = []
        # price_unit = 0.0
        for rec in self.products_line_ids:
            product = rec.product_id
            print(rec.product_amount_qty)
            product_line = (0, 0, {'product_id': rec.product_id.id,
                                   'state': 'draft',
                                   'product_uom': rec.product_id.uom_id.id,
                                   'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                   'product_uom_qty': rec.product_qty,
                                   'date_expected':fields.Datetime.now(),
                                   'name': rec.product_id.name,
                                   'cost_move': rec.product_amount_qty,
                                   'old_qty_move': rec.product_old_qty,
                                   'new_qty_move': rec.product_new_qty,
                                   'amount_qty_move': rec.product_amount_qty,
                                   'source_request_move': self.id,

                                   'employee_user_id_move': self.request_by.id,
                                   'manager_by_move': self.env.uid,

                                   })
            products_order_line.append(product_line)


        res ={
            'name': _('New Transfer'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'form',

            'target': 'new',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}},
            'view_id': view_id.id,
            'views': [(view_id.id, 'form')],

            'context': {
                'default_move_ids_without_package': products_order_line,
                'default_state': 'draft',
                'default_picking_type_id':self.operation_u_type.id,
                'default_location_id': self.Location_u_from.id,
                'default_location_dest_id': self.Location_u_to.id,
                'default_source_request': self.id,
                'default_employee_user_id': self.request_by.id,
                'default_scheduled_date':datetime.now(),
                # 'default_move_lines.date_expected':fields.Datetime.now(),

                'lang': 'en_US',
                'tz': 'Asia/Riyadh',
                'uid': self.env.user.id,

            }
        }


        return res



class stockpickUser(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_default_manager_by(self):
        return self.env['res.users'].browse(self.env.uid)

    source_request = fields.Many2one('tech.request',
                                       'Source Request',

                                       track_visibility='onchange',
                                       readonly=True)

    employee_user_id= fields.Many2one('res.users',
                                 'Employee Request',

                                 track_visibility='onchange',
                                    readonly=True)
    manager_by = fields.Many2one('res.users',
                                   'Manage by',

                                   track_visibility='onchange',
                                   default=_get_default_manager_by, readonly=True)

    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        if not self.source_request:
            if self.picking_type_id:
                if self.picking_type_id.default_location_src_id:
                    location_id = self.picking_type_id.default_location_src_id.id
                elif self.partner_id:
                    location_id = self.partner_id.property_stock_supplier.id
                else:
                    customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

                if self.picking_type_id.default_location_dest_id:
                    location_dest_id = self.picking_type_id.default_location_dest_id.id
                elif self.partner_id:
                    location_dest_id = self.partner_id.property_stock_customer.id
                else:
                    location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

                if self.state == 'draft':
                    self.location_id = location_id
                    self.location_dest_id = location_dest_id
            # TDE CLEANME move into onchange_partner_id
            if self.partner_id and self.partner_id.picking_warn:
                if self.partner_id.picking_warn == 'no-message' and self.partner_id.parent_id:
                    partner = self.partner_id.parent_id
                elif self.partner_id.picking_warn not in (
                'no-message', 'block') and self.partner_id.parent_id.picking_warn == 'block':
                    partner = self.partner_id.parent_id
                else:
                    partner = self.partner_id
                if partner.picking_warn != 'no-message':
                    if partner.picking_warn == 'block':
                        self.partner_id = False
                    return {'warning': {
                        'title': ("Warning for %s") % partner.name,
                        'message': partner.picking_warn_msg
                    }}






class userlocation(models.Model):
    _inherit ='res.users'

    location_from =fields.Many2one('stock.location',string="Location From")
    location_to = fields.Many2one('stock.location',string="Location To")
    operation_type=fields.Many2one('stock.picking.type',string="Operation type")

class stocklocationmanager(models.Model):
    _inherit = "stock.location"

    manager_ids = fields.Many2many('res.users',  string='Manager of Location')




class TechnicianRequestLine(models.Model):

    _name = "tech.request.line"
    _description = "Technician Request Line"
    _inherit = ['mail.thread']

    product_id = fields.Many2one(  'product.product', 'Product ID',
        domain=[('purchase_ok', '=', True),('type','=','product')], required=True,
        track_visibility='onchange')
    name = fields.Char('Description', size=250, track_visibility='onchange')
    product_image = fields.Binary(string="Image", related="product_id.image_medium")


    product_uom_id = fields.Many2one('uom.uom', 'Volume',    track_visibility='onchange')

    product_qty = fields.Float(string='Quantity', track_visibility='onchange', default=1,digits=dp.get_precision('Product Unit of Measure'))
    product_old_qty = fields.Float(string='Old Quantity', track_visibility='onchange',digits=dp.get_precision('Product Unit of Measure'))
    product_new_qty = fields.Float(string='new Quantity', track_visibility='onchange',digits=dp.get_precision('Product Unit of Measure'))
    product_amount_qty = fields.Float(string='amount', track_visibility='onchange',digits=dp.get_precision('Product Unit of Measure'))

    request_line_id = fields.Many2one('tech.request', 'Technician Request',     ondelete='cascade', readonly=True)
    company_id = fields.Many2one('res.company',        string='Company',      store=True, readonly=True)

    specifica = fields.Text(string='Specifications')
    iscancel = fields.Boolean(  string="Cancel", readonly=True, default=False, copy=False)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.product_image = self.product_id.image_medium
            self.name = name
            self.product_old_qty=self.product_id.qty_available
            self.product_amount_qty=self.product_id.standard_price* self.product_qty
            self.product_new_qty= self.product_old_qty-self.product_qty

    @api.onchange('product_qty')
    def onchange_product_idqty(self):
        if self.product_id and self.product_qty and self.product_old_qty :
            self.product_new_qty= self.product_old_qty-self.product_qty
            self.product_amount_qty = self.product_id.standard_price * self.product_qty

    @api.multi
    def cancel(self):
        # """Cancel a Transfer request line."""
        self.write({'iscancel': True})

    @api.multi
    def uncancel(self):
        # """UnCancel Transfer request line."""
        self.write({'iscancel': False})

    def _compute_can_editable(self):
        for rec in self:
            if rec.request_line_id.state in ('sent', 'ready',  'rejected',      'done'):
                rec.can_editable = False
            else:
                rec.can_editable = True

    can_editable = fields.Boolean(string='Can editable',
                                 compute="_compute_can_editable",
                                 readonly=True)


class SelectProducts1(models.TransientModel):

    _name = 'choose.products'

    product_ids = fields.Many2many('product.product', string='Products'
                                   ,domain=[('purchase_ok', '=', True),
                                            ('type','like','product')] ,default=[])


    @api.multi
    @api.onchange('product_ids')
    def on_change_state(self):

        for record in self.product_ids:
            print(record)

    @api.multi
    def choose_products(self):

        order_id = self.env['tech.request'].browse(self._context.get('active_id', False))
        for product in self.product_ids:

            if product:
                name = product.name
                if product.code:
                    name = '[%s] %s' % (name, product.code)
                if product.description_purchase:
                    name += '\n' + product.description_purchase

            self.env['tech.request.line'].create({
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'product_qty': 1,
                'product_image':  product.image_medium,
                'product_old_qty': product.qty_available,
                'product_new_qty': product.qty_available - 1,
                'product_amount_qty': product.standard_price ,
                'name': name,
                'request_line_id': order_id.id
            })
