# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, UserError, float_is_zero, float_compare


class HRProtection(models.Model):
    _name = 'hr.protection'
    _description = 'Employees Benefits'
    _inherit = ['mail.thread','mail.activity.mixin']

    @api.model
    def _get_Employee_request(self):
        res = self.env['res.users'].browse(self.env.uid)
        return res

    @api.multi
    def _get_default_manager_by(self):
        uid=self.env['res.users'].browse(self.env.uid)
        if uid.location_from.manager_ids:
            print("hi1111.. " , uid)
            print(uid.location_from.manager_ids)
            return uid.location_from.manager_ids
        return []


    @api.onchange('department_id')
    def get_head_Office(self):
        res=self.env['hr.department'].search([('id','=',self.department_id.id)])
        self.assigned_to=res.department_manager_id

    @api.one
    @api.depends('state')
    def _compute_can_user_approved(self):
        current_user_id = self.env.uid
        if (self.state == 'request' and current_user_id == self.assigned_to.id):
            self.can_approved = True
        else:
            self.can_approved = False

    can_approved = fields.Boolean(string='Can user approved', compute='_compute_can_user_approved')

    @api.model
    def _get_default_loc_from(self):
        uid = self.env['res.users'].browse(self.env.uid)
        return uid.location_from.id

    @api.model
    def _get_default_op_type(self):
        uid = self.env['res.users'].browse(self.env.uid)
        return uid.operation_type.id



    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    emp_id = fields.Many2one('hr.employee', required=True, string="Employee")
    request_by = fields.Many2one('res.users', 'Requested by', required=True,  track_visibility='onchange', readonly=True, default=_get_Employee_request,)
    department_id = fields.Many2one('hr.department', string='Department')
    assigned_to = fields.Many2one('res.users', 'Department Manger', track_visibility='onchange',  required=True, )
    manager_id = fields.Many2many('res.users', string='Manager of Location', default=_get_default_manager_by)
    emp_job_id = fields.Many2one('hr.job', compute="_compute_employee", store=True, readonly=True, string="Job Position")
    date_from = fields.Date("Start Date", default=fields.Date.today())
    date_to = fields.Date("End Date")
    description = fields.Text('Description')
    doc_attachment_id06 = fields.Many2many('ir.attachment', 'doc_attach_rel06', 'doc_id06','attach_id06', string="Attachment", copy=False)
    Location_u_from = fields.Many2one('stock.location', string='Location From', default=_get_default_loc_from)
    Location_u_to = fields.Many2one('stock.location', string='Location To')
    operation_u_type = fields.Many2one('stock.picking.type', string='Operation type', default=_get_default_op_type)
    state = fields.Selection([('draft','Draft'),
                              ('request','Request'),
                              ('man_approve','Manager Approve'),
                              ('approve','Approved'),
                              ('reject','Rejected'),],
                              default='draft')
    product_id = fields.Many2one('product.product', 'Product ID', domain=[('is_benefit', '=', True),('type', '=', 'product')],required=True, track_visibility='onchange')
    product_uom = fields.Char(string='Volume', compute="_get_unit", readonly=True, track_visibility='onchange')
    qty_onhand2 = fields.Float(string="On Hand", compute="_get_qty", readonly=True)
    # request_line_id = fields.Many2one('hr.protection', 'Benefit Request', ondelete='cascade', readonly=True)
    product_amount_qty = fields.Float(string='amount', track_visibility='onchange',digits=dp.get_precision('Product Unit of Measure'))
    product_qty = fields.Float(string='Quantity', track_visibility='onchange', default=1,digits=dp.get_precision('Product Unit of Measure'))
    product_old_qty = fields.Float(string='Old Quantity', track_visibility='onchange',digits=dp.get_precision('Product Unit of Measure'))
    product_new_qty = fields.Float(string='new Quantity', track_visibility='onchange',digits=dp.get_precision('Product Unit of Measure'))

    @api.depends('product_id')
    def _get_qty(self):
        for rec in self:
            rec.qty_onhand2 = rec.product_id.qty_available

    @api.depends('product_id')
    def _get_unit(self):
        for rec in self:
            rec.product_uom = rec.product_id.uom_id.name

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            self.product_old_qty = self.product_id.qty_available
            self.product_amount_qty = self.product_id.standard_price * self.product_qty
            self.product_new_qty = self.product_old_qty - self.product_qty

    @api.onchange('product_qty')
    def onchange_product_idqty(self):
        if self.product_id and self.product_qty and self.product_old_qty:
            self.product_new_qty = self.product_old_qty - self.product_qty
            self.product_amount_qty = self.product_id.standard_price * self.product_qty

###########################################################################################################################
    @api.model
    def create(self, vals):
        # assigning the sequence for the record
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.protection') or _('New')
        res = super(HRProtection, self).create(vals)
        return res

    @api.depends('emp_id')
    def _compute_employee(self):
        for i in self.filtered('emp_id'):
            i.emp_job_id = i.emp_id.job_id



    # def make_activity(self, user_ids):
    #     print("j...", user_ids)
    #     now = datetime.now()
    #     date_deadline = now.date()
    #
    #     if self:
    #         if user_ids:
    #             actv_id = self.sudo().activity_schedule(
    #                 'mail.mail_activity_data_todo', date_deadline,
    #                 note=_(
    #                     '<a href="#" data-oe-model="%s" data-oe-id="%s">Task </a> for <a href="#" data-oe-model="%s" data-oe-id="%s">%s\'s</a> Review') % (
    #                          self._name, self.id, self.emp_id._name,
    #                          self.emp_id.id, self.emp_id.display_name),
    #                 user_id=user_ids,
    #                 res_id=self.id,
    #
    #                 summary=_("Request Approve")
    #             )
    #             print("active", actv_id)

    # def _send_email_request(self,user_group,sub,content):
    #     recipient_partners = []
    #     for group in user_group:
    #         print('asd1')
    #         for recipient in group.users:
    #             print(recipient)
    #             if recipient.partner_id.id not in recipient_partners:
    #                 recipient_partners.append(recipient.partner_id.id)
    #     if len(recipient_partners):
    #         print(recipient_partners)
    #         self.message_post(body=content,
    #                        subtype='mt_comment',
    #                        subject=sub,
    #                        partner_ids=recipient_partners,
    #                        message_type='comment')

    @api.multi
    def emp_request_action(self):
        available_qty = self.product_id.qty_available
        if available_qty < self.product_qty:
            raise UserError(_('product qty not enough for your order  ' + str(self.product_id.name)))

        sub = _("Employee Benefit Request - Department Manager")
        content = _("Hello,<br>Mr/Mrs: <b>" + str(self.emp_id.name) + "</b> Has a Benefit request with Ref: <b>" + str(self.name) +  "</b> requires your approve," \
                    "<br>May you check it please.. ")
        recipient_partners = []
        if self.assigned_to:
            recipient_partners.append(self.assigned_to.partner_id.id)
            if len(recipient_partners):
                print(recipient_partners)
                self.message_post(body=content,
                                  subtype='mt_comment',
                                  subject=sub,
                                  partner_ids=recipient_partners,
                                  message_type='comment')
        return self.write({'state': 'request'})

#########################################################################################################################

    @api.multi
    def hr_manager_action(self):
        # user_group = self.env.ref("sales_team.group_sale_manager")
        # print("yes1235", user_group)
        # sub = _("Employee Benefit Request - Stock Manger")
        # content = _("Hello,<br>Mr/Mrs: <b>" + str(
        #     self.emp_id.name) + "</b> Has a <b>Benefit</b> request  request with Ref: <b>" + str(
        #     self.name) + "</b> requires your Processing," \
        #                  "<br>May you check it please.. ")
        # i = self._send_email_request(user_group, sub, content)

        recipient_partners = []
        msg_sub = "Employee Benefit Request - Stock Manager"
        msg_body = _("Hello,<br>Mr/Mrs: <b>" + str(self.emp_id.name) + "</b> Has a Benefit request with Ref: <b>" + str(self.name) + "</b> requires your approve," \
                         "<br>May you check it please.. ")
        # if self.request_by.partner_id.id and self.request_by.partner_id.id not in recipient_partners:
        #     recipient_partners.append(self.request_by.partner_id.id)
        # if self.manager_id:
        #     for m in self.manager_id:
        #         if m.partner_id.id not in recipient_partners:
        #             recipient_partners.append(m.partner_id.id)

        if self.department_id.create_quotation_manager_id:
            recipient_partners.append(self.department_id.create_quotation_manager_id.partner_id.id)
            print(recipient_partners)

            if len(recipient_partners):
                self.message_post(body=msg_body,
                                  subtype='mt_comment',
                                  subject=msg_sub,
                                  partner_ids=recipient_partners,
                                  message_type='comment')



        # sub = _("Employee Benefit Request - Stock Manager")
        # content = _("Hello,<br>Mr/Mrs: <b>" + str(self.emp_id.name) + "</b> Has a Benefit request with Ref: <b>" + str(self.name) +  "</b> requires your approve," \
        #             "<br>May you check it please.. ")
        # recipient_partners = []
        # groups = self.env['res.groups'].search([('name', '=', 'Technician Request Manager')])
        # for group in groups:
        #     for recipient in group.users:
        #         print(recipient)
        #         if recipient.partner_id.id not in recipient_partners:
        #             recipient_partners.append(recipient.partner_id.id)
        #     if len(recipient_partners):
        #         print(recipient_partners)
        #         self.message_post(body=content,
        #                           subtype='mt_comment',
        #                           subject=sub,
        #                           partner_ids=recipient_partners,
        #                           message_type='comment')
        return self.write({'state': 'man_approve'})

    @api.multi
    def hr_administrator_action(self):
        view_id = self.env.ref('stock.view_picking_form')
        products_order_line = []
        product_line = {'product_id': self.product_id.id,
                        'state': 'draft',
                        'product_uom': self.product_id.uom_id.id,
                        'product_uom_qty': self.product_qty,
                        'date_expected': fields.Datetime.now(),
                        'name': self.product_id.name,
                        'cost_move': self.product_amount_qty,
                        'old_qty_move': self.product_old_qty,
                        'new_qty_move': self.product_new_qty,
                        'amount_qty_move': self.product_amount_qty,
                        'employee_user_id_move': self.request_by.id,
                        # 'manager_by_move': self.env.uid,
                        # 'manager_by_move': self.manager_by,
                        }
        products_order_line.append(product_line)

        res = {
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
            # 'default_picking_type_id': self.operation_u_type.id,
            'default_picking_type_id':37,
            'default_location_id': self.Location_u_from.id,
            'default_location_dest_id': 99,
            'default_benefit_id': self.id,
            # 'default_origin': self.name,
            'default_employee_user_id': self.request_by.id,
            'default_employee_id': self.emp_id.id,
            'manager_by': self.manager_id,
            'default_scheduled_date': datetime.now(),
            'default_move_lines.date_expected':fields.Datetime.now(),
            'lang': 'en_US',
            'tz': 'Asia/Riyadh',
            # 'uid': self.env.user.id,

            }
        }
        # user_group = self.env.ref("hr.group_hr_manager")
        # sub = _("Employee Benefit Request - HrAdmin")
        # content = _("Hello,<br>Mr/Mrs: <b>" + str(self.emp_id.name) + "</b> Has a <b>Benefit</b> request requires your approve,"\
        #                "<br>May you check it please.. ")
        #
        # self._send_email_request(user_group,sub,content)

        # if products_order_line:
        self.write({'state': 'approve'})
        return res
##########################################################################################################################
    @api.multi
    def reject_action(self):
        return self.write({'state': 'reject'})

    @api.multi
    def reset_action(self):
        return self.write({'state': 'draft'})


class HrProtectionAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel06 = fields.Many2many('hr.protection', 'doc_attachment_id06', 'attach_id06', 'doc_id06',
                                        string="Attachment", invisible=1)



class BenefitRequestLine(models.Model):

    _name = "benefit.request.line"
    _description = "Benefits Request Line"
    _inherit = ['mail.thread']
######################################################3

class stockpickUser(models.Model):
    _inherit = 'stock.picking'

    benefit_id = fields.Many2one('hr.protection', string="Benefit Request")
    employee_id = fields.Many2one('hr.employee',  string="Employee Benefit Request")


class benbfiteproducte(models.Model):
    _inherit = 'product.template'

    is_benefit = fields.Boolean(string = 'This Product is Benefit')


    def benefits_button(self):
        self.ensure_one()
        domain = [
            ('product_id.name', '=', self.name)]
        print('yes', domain)

        return {
                'name': _('Benefits'),
                'domain': domain,
                'res_model': 'hr.protection',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'tree,form',
                'view_type': 'form',
                'help': _('''<p class="oe_view_nocontent_create">
                                       Click To Create For New Records
                                    </p>'''),
                'limit': 80,
                'context': "{'default_product_id.name': %s}" % self.id,}

    def _document_count_protection(self):
        for each in self:
            document_ids2 = self.env['hr.protection'].sudo().search([('product_id.name', '=', each.name)])
            each.document_count_protection = len(document_ids2)
            # print(document_ids2.emp_id.name)
            print(self.name)
    document_count_protection = fields.Integer(compute='_document_count_protection')












