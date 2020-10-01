# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
from odoo.tools import pycompat, ustr, formataddr
from odoo import api, fields, models, _ , SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from requests import exceptions

_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('leader_approved', 'Leader Approved'),
    ('manager_approved', 'Manager Approved'),
    ('done', 'Done'),
    ('rejected', 'Rejected')
]


class SprogroupPurchaseRequest(models.Model):

    _name = 'sprogroup.purchase.request'
    _description = 'Sprogroup Purchase Request'
    _inherit = ['mail.thread']


    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('sprogroup.purchase.request')

    name = fields.Char('Request Name', size=32, required=True, track_visibility='onchange')
    code = fields.Char('Code', size=32, required=True, default=_get_default_name, track_visibility='onchange')
    date_start = fields.Date('Start date',
                             help="Date when the user initiated the request.",
                             default=fields.Date.context_today,
                             track_visibility='onchange')
    end_start = fields.Date('End date',default=fields.Date.context_today,
                             track_visibility='onchange')
    requested_by = fields.Many2one('res.users',
                                   'Requested by',
                                   required=True,
                                   track_visibility='onchange',
                                   default=_get_default_requested_by)
    employee_name = fields.Many2one('hr.employee','Employee Name') #, domain=[('supplier','=',False) ,('customer','=',False) ]
    assigned_to = fields.Many2one('res.users', 'Approver', required=True,
                                  track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', 'Vendor', required=True, domain=[('supplier','=',True) ])
    description = fields.Text('Description')

    line_ids = fields.One2many('sprogroup.purchase.request.line', 'request_id',
                               'Products to Purchase',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')
    is_editable_employee_name = fields.Boolean(string='Is editable emp Name',default=True)


    @api.onchange('state')
    def onchange_state(self):
        assigned_to = None
        if self.state:
            if (self.requested_by.id == False):
                self.assigned_to = None
                return

        #     employee = self.env['hr.employee'].search([('work_email', '=', self.requested_by.email)])
        #     if(len(employee) > 0):
        #         if(employee[0].department_id and employee[0].department_id.manager_id):
        #             assigned_to = employee[0].department_id.manager_id.user_id
        #
        # self.assigned_to =  assigned_to

    @api.multi
    # @api.depends('requested_by')
    @api.onchange('requested_by')
    def _compute_department(self):
        if (self.requested_by.id == False):
            self.department_id = False
            return

        employee = self.env['hr.employee'].search([('work_email', '=', self.requested_by.login)])
        if (len(employee) > 0):
            self.department_id = employee[0].department_id.id
        else:
            self.department_id = False

    department_id = fields.Many2one('hr.department', string='Department')

    @api.one
    @api.depends('state')
    def _compute_can_leader_approved(self):
        current_user_id = self.env.uid
        if(self.state == 'to_approve' and current_user_id == self.assigned_to.id):
            self.can_leader_approved = True
        else:
            self.can_leader_approved = False
    can_leader_approved = fields.Boolean(string='Can Leader approved',compute='_compute_can_leader_approved' )

    @api.one
    @api.depends('state')
    def _compute_can_manager_approved(self):
        current_user = self.env['res.users'].browse(self.env.uid)

        if (self.state == 'leader_approved' and current_user.has_group('sprogroup_purchase_request.group_sprogroup_purchase_request_manager')):
            self.can_manager_approved = True
        else:
            self.can_manager_approved = False

    can_manager_approved = fields.Boolean(string='Can Manager approved',compute='_compute_can_manager_approved')


    @api.one
    @api.depends('state')
    def _compute_can_reject(self):
        self.can_reject = (self.can_leader_approved or self.can_manager_approved)

    can_reject = fields.Boolean(string='Can reject',compute='_compute_can_reject')

    @api.multi
    @api.depends('state')
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ('to_approve', 'leader_approved','manager_approved', 'rejected', 'done'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    is_editable = fields.Boolean(string="Is editable",
                                 compute="_compute_is_editable",
                                 readonly=True)


    @api.onchange('department_id')
    def get_head_Office(self):
        res=self.env['hr.department'].search([('id','=',self.department_id.id)])
        self.assigned_to=res.department_manager_id



    @api.model
    def create(self, vals):
        request = super(SprogroupPurchaseRequest, self).create(vals)
        if vals.get('assigned_to'):
            request.message_subscribe(partner_ids=[request.assigned_to.partner_id.id])
        return request

    @api.multi
    def write(self, vals):
        res = super(SprogroupPurchaseRequest, self).write(vals)
        for request in self:
            if vals.get('assigned_to'):
                self.message_subscribe(partner_ids=[request.assigned_to.partner_id.id])
        return res

    @api.multi
    def button_draft(self):
        self.mapped('line_ids').do_uncancel()
        return self.write({'state': 'draft'})


    @api.multi
    def button_to_approve(self):

        self.is_editable_employee_name=False
        # partners = self.env['res.users'].search([])
        # for m in partners:
        #     print(m.name,m.partner_id.id )

        recipient_partners = []
        if self.assigned_to.partner_id.id and self.assigned_to.partner_id.id not in recipient_partners:
            recipient_partners.append(self.assigned_to.partner_id.id)
        # if self.requested_by.partner_id.id and self.requested_by.partner_id.id not in recipient_partners:
        #     recipient_partners.append(self.requested_by.partner_id.id)
        # # recipient_partners.append(4424)

        # if self.employee_name.id and self.employee_name.id not in recipient_partners:
        #             recipient_partners.append(self.employee_name.work_email)

        print("hi",recipient_partners)

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)

        #########
        # mo. edit
        #########

        msg_body = "<b>New purchase request require your approval</b><br>" \
                   + "<div><a style='padding: 10px;font-size: 15px;color: #ffffff;text-decoration: none !important;font-weight: bold;background-color: #875a7b !important;border: 0px solid #875a7b;border-radius: 3px;' href=" + str(
            base_url) + ">Check From Here</a></div>" \
                   + "<br><b>Request Name:</b> " + str(self.name) + " / " + str(self.code) \
                   + "<b><br>Requested By:</b> " + str(self.requested_by.name) \
                   + "<b><br>Employee Name: </b>" + str(self.employee_name.name) \
                   + "<b><br>Vendor: </b>" + str(self.partner_id.name) \
                   + "<b><br>Department: </b>" + str(self.department_id.name) \
                   + "<b><br>Start/End Date: </b>" + str(self.date_start) + " : " + str(self.end_start)



        activities = {}
        list = []
        task_description = ""
        total=0
        for i in self.line_ids:
            # total += i.product_qty
            activities.update(
                {'Product': i.product_id.name, 'Description': i.name,
                 'Quantity': i.product_qty, 'Request Date': i.date_required})
            list.append(activities)
            task_description += "<tr>   <td  align=""center""> <font size=""2"">{3}</font></td>" \
                                "<td  align=""center""> <font size=""2"">{2}</font></td>" \
                                "<td  align=""center""> <font size=""2"">{1}</font></td>    " \
                                "<td  align=""center""> <font size=""2"">{0}</font></td>  </tr>" \
                .format(str(i.date_required),str(i.product_qty),str(i.name),str(i.product_id.name),)

            print(task_description)

            status_table = " <font size=""2"">   <p> {0}<br>---------------------------- </p>" \
                           "<table style=""width:80%"" border="" 1px solid black"">" \
                           "<tr> <th><font size=""2"">Product</font> </th>    " \
                           "<th><font size=""2"">Description</font> </th>    " \
                           "<th><font size=""2"">Quantity</font> </th>    " \
                           "<th><font size=""2"">Request Date</font> </th>    </tr>{1}" \
                           "</table>" \
                           "<p> <p>Regards,</p> </font>" \
                .format(msg_body,task_description, i.date_required, i.product_qty, i.name, i.product_id.name)
            print(status_table)
        msg_sub = "Approve Purchase Request" + " / " + self.name + "/" + self.code \
                  + " / " + self.requested_by.name + " / " + self.state
        ##########
        # mo. edit
        ##########
        if len(recipient_partners):
            current = self.browse(self._context.get('active_id', False))
            current.message_post(body=status_table,
                                 subtype='mt_comment',
                                 subject=msg_sub,
                                 partner_ids=recipient_partners,
                                 message_type='comment')
        return self.write({'state': 'to_approve'})

    # @api.multi
    # def button_leader_approved(self):
    # return self.write({'state': 'leader_approved'})


    @api.multi
    def button_manager_approved(self):
        return self.write({'state': 'done'})



    @api.multi
    def button_rejected(self):
        self.mapped('line_ids').do_cancel()
        return self.write({'state': 'rejected'})

    # @api.multi
    # def button_done(self):
    #     return self.write({'state': 'done'})

    @api.multi
    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({'state': 'rejected'})
    def get_partners(self):
        all_data={'recipient_partners':[],'Subject':"", "Body":""}
        res_conf = self.env['res.config.settings'].sudo()
        recipient_partners = []
        max_manager = res_conf.get_values()
        # print(max_manager['maximum_amount_leader'])
        # print(max_manager['maximum_amount'])
        # print(self.amount_total)
        all_data['Subject'] = "Purchase Order "+str(self.name)
        all_data['Body'] = "This Purchase Order Need Approve from you"
        # all_data['recipient_partners'].append(self.Approver_leader_id.partner_id.id)
        if self.need_CEO_Approve != True and max_manager['maximum_amount'] > self.amount_total:
            if max_manager['maximum_amount_leader'] > self.amount_total:
                all_data ['recipient_partners'].append(self.Approver_leader_id.partner_id.id )


            else:
                all_data ['recipient_partners'].append(self.Approver_leader_id.partner_id.id)
                # all_data ['recipient_partners'].append(299) #ibrahim parner_id

        else:
            all_data ['recipient_partners'].append(self.Approver_leader_id.partner_id.id)
            # all_data ['recipient_partners'].append(299)  # ibrahim parner_id
            # all_data ['recipient_partners'].append(298)  # Prince parner_id

        print(all_data)
        return all_data

    def send_m(self,msubj="",mbody=""):
        dic=self.get_partners()
        print(dic)
        recipient_partners = dic["recipient_partners"]

        msgsubject= dic["Subject"]
        msgbody = dic["Body"]
        if msubj != "":
            msgsubject = msubj

        if mbody != "":
            msgbody = mbody
        ###########
        # mo. edit
        ###########
        msg_body = "<b>New purchase request require your approval</b>" + "<br><b>Request Name:</b> " + str(
            self.name) + " / " + str(self.code) \
                   + "<b><br>Requested By:</b> " + str(self.requested_by.name) \
                   + "<b><br>Employee Name: </b>" + str(self.employee_name.name) \
                   + "<b><br>Vendor: </b>" + str(self.partner_id.name) \
                   + "<b><br>Department: </b>" + str(self.department_id.name) \
                   + "<b><br>Start/End Date: </b>" + str(self.date_start) + " : " + str(self.end_start)

        activities = {}
        list = []
        task_description = ""
        total = 0
        for i in self.line_ids:
            # total += i.product_qty
            activities.update(
                {'Product': i.product_id.name, 'Description': i.name,
                 'Quantity': i.product_qty, 'Request Date': i.date_required})
            list.append(activities)
            task_description += "<tr>   <td  align=""center""> <font size=""2"">{3}</font></td>" \
                                "<td  align=""center""> <font size=""2"">{2}</font></td>" \
                                "<td  align=""center""> <font size=""2"">{1}</font></td>    " \
                                "<td  align=""center""> <font size=""2"">{0}</font></td>  </tr>" \
                .format(str(i.date_required), str(i.product_qty), str(i.name), str(i.product_id.name), )

            print(task_description)

            status_table = " <font size=""2"">   <p> {0}<br>---------------------------- </p>" \
                           "<table style=""width:80%"" border="" 1px solid black"">" \
                           "<tr> <th><font size=""2"">Product</font> </th>    " \
                           "<th><font size=""2"">Description</font> </th>    " \
                           "<th><font size=""2"">Quantity</font> </th>    " \
                           "<th><font size=""2"">Request Date</font> </th>    </tr>{1}" \
                           "</table>" \
                           "<p> <p>Regards,</p> </font>" \
                .format(msg_body, task_description, i.date_required, i.product_qty, i.name, i.product_id.name)
            print(status_table)

        msg_sub = "Approve Purchase Request" + " / " + self.name + "/" + self.code \
                  + " / " + self.requested_by.name + " / " + self.state
        ###########
        # mo. edit
        ###########


        # if self.assigned_to.partner_id.id and self.assigned_to.partner_id.id not in recipient_partners:
        #     recipient_partners.append(self.assigned_to.partner_id.id)
        # if self.requested_by.partner_id.id and self.requested_by.partner_id.id not in recipient_partners:
        #     recipient_partners.append(self.requested_by.partner_id.id)
        # # recipient_partners.append(4424)

        # if self.employee_name.id and self.employee_name.id not in recipient_partners:
        #             recipient_partners.append(self.employee_name.work_email)

        print(recipient_partners)

        if len(recipient_partners):
            self.message_post(body=msgbody+status_table,
                              subtype='mt_comment',
                              subject=msgsubject+msg_sub,
                              partner_ids=recipient_partners,
                              message_type='comment')

    @api.multi
    def make_purchase_quotation(self):
        view_id = self.env.ref('purchase.purchase_order_form')

        # vals = {
        #     'partner_id': partner.id,
        #     'picking_type_id': self.rule_id.picking_type_id.id,
        #     'company_id': self.company_id.id,
        #     'currency_id': partner.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id,
        #     'dest_address_id': self.partner_dest_id.id,
        #     'origin': self.origin,
        #     'payment_term_id': partner.property_supplier_payment_term_id.id,
        #     'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        #     'fiscal_position_id': fpos,
        #     'group_id': group
        # }

        order_line = []
        price_unit = 0.0
        for line in self.line_ids:
            if line.product_id.seller_ids:
                # print(">>>>>>>>>>", line.product_id.seller_ids)
                for r in line.product_id.seller_ids:
                    # print("LLLLLLLL", r.name.name)
                    if r.name.id == self.partner_id.id:
                        price_unit = r.price
                # raise UserError(_(">>>>>>>>>>"))
            product = line.product_id
            fpos = self.env['account.fiscal.position']
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.user.company_id.id
                taxes_id = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
            else:
                taxes_id = fpos.map_tax(line.product_id.supplier_taxes_id)

            product_line = (0, 0, {'product_id' : line.product_id.id,
                                   'state' : 'draft',
                                   'product_uom' : line.product_id.uom_po_id.id,
                                    'price_unit' : price_unit,
                                   'date_planned' :  datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                   # 'taxes_id' : ((6,0,[taxes_id.id])),
                                   'product_qty' : line.product_qty,
                                   'name' : line.product_id.name,
                                   })
            order_line.append(product_line)

        # vals = {
        #     # 'order_line' : order_line
        #
        # }
        #
        # po = self.env['purchase.order'].create(vals)
        #

        return {
            'name': _('New Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'form',

            'target': 'new',
            'view_id': view_id.id,
            'views': [(view_id.id, 'form')],

            'context': {
                'default_order_line': order_line,
                'default_state': 'draft',
                'default_partner_id': self.partner_id.id,
                'default_purchase_request_id': self.id,
                'default_employee_name_id': self.employee_name.id,
                'default_Approver_leader_id': self.assigned_to.id,
                'lang': 'en_US',
                'tz': 'Asia/Riyadh',
                'uid': self.env.user.id,

            }
        }

class purchaseorderwizard(models.Model):
    _inherit='purchase.order'

    purchase_request_id=fields.Many2one('sprogroup.purchase.request','Purchase Request')
    employee_name_id=fields.Many2one('hr.employee','Employee Name')
    Approver_leader_id =fields.Many2one('res.users','Aprover Name')


class department_headOffice(models.Model):
    _inherit ='hr.department'

    department_manager_id=  fields.Many2one('res.users', 'Head Office',required=True, track_visibility='onchange')




class SprogroupPurchaseRequestLine(models.Model):

    _name = "sprogroup.purchase.request.line"
    _description = "Sprogroup Purchase Request Line"
    _inherit = ['mail.thread']

    @api.multi
    @api.depends('product_id', 'name', 'product_uom_id', 'product_qty',
                  'date_required', 'specifications')


    @api.multi
    def _compute_supplier_id(self):
        for rec in self:
            if rec.product_id:
                if rec.product_id.seller_ids:
                    rec.supplier_id = rec.product_id.seller_ids[0].name



    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('purchase_ok', '=', True)], required=True,
        track_visibility='onchange')
    name = fields.Char('Description', size=256,
                       track_visibility='onchange')
    product_uom_id = fields.Many2one('uom.uom', 'Volume',
                                     track_visibility='onchange')
    product_qty = fields.Float(string='Quantity', track_visibility='onchange', digits=dp.get_precision('Product Unit of Measure'))
    request_id = fields.Many2one('sprogroup.purchase.request',
                                 'Purchase Request',
                                 ondelete='cascade', readonly=True)
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 store=True, readonly=True)

    requested_by = fields.Many2one('res.users',
                                   related='request_id.requested_by',
                                   string='Requested by',
                                   store=True, readonly=True)
    assigned_to = fields.Many2one('res.users',
                                  related='request_id.assigned_to',
                                  string='Assigned to',
                                  store=True, readonly=True)
    date_start = fields.Date(related='request_id.date_start',
                             string='Request Date', readonly=True,
                             store=True)
    end_start = fields.Date(related='request_id.end_start',
                             string='End Date', readonly=True,
                             store=True)
    description = fields.Text(related='request_id.description',
                              string='Description', readonly=True,
                              store=True)
    date_required = fields.Date(string='Request Date', required=True,
                                track_visibility='onchange',
                                default=fields.Date.context_today)

    specifications = fields.Text(string='Specifications')
    request_state = fields.Selection(string='Request state',
                                     readonly=True,
                                     related='request_id.state',
                                     selection=_STATES,
                                     store=True)
    supplier_id = fields.Many2one('res.partner',
                                  string='Preferred supplier',
                                  compute="_compute_supplier_id")

    cancelled = fields.Boolean(
        string="Cancelled", readonly=True, default=False, copy=False)

    # volume_id = fields.Many2one(comodel_name="uom.uom", string="Volume")

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
            self.name = name

    @api.multi
    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({'cancelled': True})

    @api.multi
    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({'cancelled': False})

    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ('to_approve', 'leader_approved','manager_approved',  'rejected',
                                        'done'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    is_editable = fields.Boolean(string='Is editable',
                                 compute="_compute_is_editable",
                                 readonly=True)

    @api.multi
    def write(self, vals):
        res = super(SprogroupPurchaseRequestLine, self).write(vals)
        if vals.get('cancelled'):
            requests = self.mapped('request_id')
            requests.check_auto_reject()
        return res

class MailThreadInherit(models.AbstractModel):
    _inherit = 'mail.thread'


    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, body='', subject=None,
                     message_type='notification', subtype=None,
                     parent_id=False, attachments=None,
                     notif_layout=False, add_sign=True, model_description=False,
                     mail_auto_delete=True, **kwargs):
        """ Post a new message in an existing thread, returning the new
            mail.message ID.
            :param int thread_id: thread ID to post into, or list with one ID;
                if False/0, mail.message model will also be set as False
            :param str body: body of the message, usually raw HTML that will
                be sanitized
            :param str type: see mail_message.message_type field
            :param int parent_id: handle reply to a previous message by adding the
                parent partners to the message in case of private discussion
            :param tuple(str,str) attachments or list id: list of attachment tuples in the form
                ``(name,content)``, where content is NOT base64 encoded
            Extra keyword arguments will be used as default column values for the
            new mail.message record. Special cases:
                - attachment_ids: supposed not attached to any document; attach them
                    to the related document. Should only be set by Chatter.
            :return int: ID of newly created mail.message
        """
        if attachments is None:
            attachments = {}
        if self.ids and not self.ensure_one():
            raise exceptions.Warning(_('Invalid record set: should be called as model (without records) or on single-record recordset'))

        # if we're processing a message directly coming from the gateway, the destination model was
        # set in the context.


        model = False
        if self.ids:
            self.ensure_one()
            model = kwargs.get('model', False) if self._name == 'mail.thread' else self._name
            if model and model != self._name and hasattr(self.env[model], 'message_post'):
                return self.env[model].browse(self.ids).message_post(
                    body=body, subject=subject, message_type=message_type,
                    subtype=subtype, parent_id=parent_id, attachments=attachments,
                    notif_layout=notif_layout, add_sign=add_sign,
                    mail_auto_delete=mail_auto_delete, model_description=model_description, **kwargs)



        # 0: Find the message's author, because we need it for private discussion
        author_id = kwargs.get('author_id')
        if author_id is None:  # keep False values
            author_id = self.env['mail.message']._get_default_author().id


        # 2: Private message: add recipients (recipients and author of parent message) - current author
        #   + legacy-code management (! we manage only 4 and 6 commands)
        partner_ids = set()
        kwargs_partner_ids = kwargs.pop('partner_ids', [])
        for partner_id in kwargs_partner_ids:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                partner_ids.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                partner_ids |= set(partner_id[2])
            elif isinstance(partner_id, pycompat.integer_types):
                partner_ids.add(partner_id)
            else:
                pass  # we do not manage anything else
        if parent_id and not model:
            parent_message = self.env['mail.message'].browse(parent_id)
            private_followers = set([partner.id for partner in parent_message.partner_ids])
            if parent_message.author_id:
                private_followers.add(parent_message.author_id.id)
            private_followers -= set([author_id])
            partner_ids |= private_followers

        # 4: mail.message.subtype
        subtype_id = kwargs.get('subtype_id', False)
        if not subtype_id:
            subtype = subtype or 'mt_note'
            if '.' not in subtype:
                subtype = 'mail.%s' % subtype
            subtype_id = self.env['ir.model.data'].xmlid_to_res_id(subtype)

        # automatically subscribe recipients if asked to
        if self._context.get('mail_post_autofollow') and self.ids and partner_ids:
            partner_to_subscribe = partner_ids
            if self._context.get('mail_post_autofollow_partner_ids'):
                partner_to_subscribe = [p for p in partner_ids if p in self._context.get('mail_post_autofollow_partner_ids')]
            self.message_subscribe(list(partner_to_subscribe))

        # _mail_flat_thread: automatically set free messages to the first posted message
        MailMessage = self.env['mail.message']
        if self._mail_flat_thread and model and not parent_id and self.ids:
            messages = MailMessage.search(['&', ('res_id', '=', self.ids[0]), ('model', '=', model)], order="id ASC", limit=1)
            parent_id = messages.ids and messages.ids[0] or False
        # we want to set a parent: force to set the parent_id to the oldest ancestor, to avoid having more than 1 level of thread
        elif parent_id:
            messages = MailMessage.sudo().search([('id', '=', parent_id), ('parent_id', '!=', False)], limit=1)
            # avoid loops when finding ancestors
            processed_list = []
            if messages:
                message = messages[0]
                while (message.parent_id and message.parent_id.id not in processed_list):
                    processed_list.append(message.parent_id.id)
                    message = message.parent_id
                parent_id = message.id

        #############
        # mo. start lognote payments

        payments_ids2 = self._name
        if payments_ids2 == 'account.payment':
            payments_ids = self.env['account.payment'].browse(self.ids)

            lognote_sub = "{0} / {1} / {2} / {3} / {4}" \
                .format(payments_ids.name, payments_ids.partner_type, payments_ids.partner_id.name,
                        payments_ids.amount, payments_ids.payment_date)

            lognote_body = "<b><br>---------------Details---------------</b>" \
                           "<br><b>Partner Name:</b> {0}" \
                           "<br><b>Partner Type:</b> {1}" \
                           "<br><b>Payment Name:</b> {2}" \
                           "<br><b>Payment Amount:</b> {3}" \
                           "<br><b>Payment Journal:</b> {4}" \
                           "<br><b>Payment Date:</b> {5}" \
                           "<br><b>Memo:</b> {6}" \
                .format(payments_ids.partner_id.name, payments_ids.partner_type,
                        payments_ids.name, payments_ids.amount,
                        payments_ids.journal_id.name, payments_ids.payment_date,
                        payments_ids.communication, )


        if payments_ids2 == 'account.payment':
            values = kwargs
            values.update({
                'author_id': author_id,
                'model': model,
                'res_id': model and self.ids[0] or False,
                'body': body + lognote_body,
                'subject': lognote_sub or False,
                'message_type': message_type,
                'parent_id': parent_id,
                'subtype_id': subtype_id,
                'partner_ids': [(4, pid) for pid in partner_ids],
                'channel_ids': kwargs.get('channel_ids', []),
                'add_sign': add_sign
            })
            if notif_layout:
                values['layout'] = notif_layout

        # mo. end lognote payments
        #############

        else:
            values = kwargs
            values.update({
                'author_id': author_id,
                'model': model,
                'res_id': model and self.ids[0] or False,
                'body': body,
                'subject': subject or False,
                'message_type': message_type,
                'parent_id': parent_id,
                'subtype_id': subtype_id,
                'partner_ids': [(4, pid) for pid in partner_ids],
                'channel_ids': kwargs.get('channel_ids', []),
                'add_sign': add_sign
            })
            if notif_layout:
                values['layout'] = notif_layout


        # 3. Attachments
        #   - HACK TDE FIXME: Chatter: attachments linked to the document (not done JS-side), load the message
        attachment_ids = self._message_post_process_attachments(attachments, kwargs.pop('attachment_ids', []), values)
        values['attachment_ids'] = attachment_ids

        # Avoid warnings about non-existing fields
        for x in ('from', 'to', 'cc'):
            values.pop(x, None)

        # Post the message
        # canned_response_ids are added by js to be used by other computations (odoobot)
        # we need to pop it from values since it is not stored on mail.message
        canned_response_ids = values.pop('canned_response_ids', False)
        new_message = MailMessage.create(values)
        values['canned_response_ids'] = canned_response_ids
        self._message_post_after_hook(new_message, values, model_description=model_description, mail_auto_delete=mail_auto_delete)
        return new_message


