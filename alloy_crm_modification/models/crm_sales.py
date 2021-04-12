# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import datetime, timedelta
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_order_line_ids = fields.One2many(comodel_name="crm.lead.order.line", inverse_name="crm_lead_id", string="order lines")
    logistic_user_id = fields.Many2one(comodel_name="res.users")
    agency_location_id = fields.Many2one(comodel_name="generic.location")
    car_type_id = fields.Many2one(comodel_name="vehicle")
    is_insured = fields.Boolean(string="insured")
    is_company = fields.Boolean(compute='get_type_of_partner_id')
    is_lost = fields.Boolean(string='get_lost1')
    is_lost_blue =fields.Boolean(string="is lost Blue",default=False)
    is_lost_green =fields.Boolean(string="is lost green" ,default=False)
    claim_number = fields.Char(string="Claim #")
    crm_source_id = fields.Many2one(comodel_name="sale.order.source", string="source",)
    city_id = fields.Many2one('res.city', 'City')
    sales_id=fields.Many2one('sale.order', string='Quotation/SO')

    # @api.model
    # def get_lost(self):
    #     b = False
    #     for rec in self:
    #         print(rec.sales_id)
    #         print(rec.sales_id.name)
    #         print(rec.sales_id.date_order)
    #         print(rec.sales_id.offer_valid)
    #         if rec.sales_id.date_order:
    #             date1 = rec.sales_id.date_order
    #             date2 = fields.Datetime.now()
    #             print("date1",date1)
    #             print(date2)
    #
    #             # code to get hours and minutes
    #             datetimeFormat = '%Y-%m-%d %H:%M:%S'
    #             date11 = datetime.strptime(str(date1), datetimeFormat)
    #
    #             date12 = datetime.strptime(str(date2), datetimeFormat)
    #
    #             diff = date12 - date11
    #             hour1 = diff.days * 24
    #
    #             hours = (diff.seconds) // 3600
    #             minutes = ((diff.seconds) % 3600) // 60
    #             totalhours = hour1 + hours
    #             # task.task_hours =totalhours
    #
    #             if rec.sales_id.offer_valid == '24hrs' :
    #                 if totalhours > 24:
    #                     b=True
    #                     print('lost24')
    #             elif   rec.sales_id.offer_valid == '3days' :
    #                 if totalhours > 72:
    #                     b=True
    #                     print('lost72')
    #             elif  rec.sales_id.offer_valid == '1Week':
    #                 if totalhours > 168:
    #                     b = True
    #                     print('lost168')
    #
    #             elif rec.sales_id.offer_valid == '2Week':
    #                 if totalhours > 336:  #336
    #                     b = True
    #                     print('lost336')
    #
    #             if totalhours > 336:  # 336
    #                 b = True
    #                 rec.is_lost_blue = True
    #             print(totalhours)
    #             print(b)
    #             rec.is_lost = b
    #
    #             stage = self.env['crm.stage'].search([('name', '=', 'Lost')])
    #             print(stage.name)
    #             for record in rec:
    #                 print(record.is_lost)
    #                 if record.is_lost == True:
    #                     if stage:
    #                         record.stage_id= stage.id
    #                         record.write({'stage_id': stage.id})
    #                         record.write({'is_lost': True })
    #
    #
    #     return b

    @api.multi
    def review_all_lead(self):
        crm_leads_ids = self.search([])
        print(crm_leads_ids)
        print("haytham Fadar")
        stage = self.env['crm.stage'].search([('name', '=', 'Lost')])
        for record in crm_leads_ids:
            print(record.name)
            b = False
            for rec in record:
                print(rec.sales_id)
                for myrec in rec.sales_id:
                    print(myrec.name)
                    print(myrec.state)
                    if myrec.date_order:
                        date1 = myrec.date_order
                        date2 = fields.Datetime.now()
                        print("date1", date1)
                        print(date2)

                        # code to get hours and minutes
                        datetimeFormat = '%Y-%m-%d %H:%M:%S'
                        date11 = datetime.strptime(str(date1), datetimeFormat)

                        date12 = datetime.strptime(str(date2), datetimeFormat)

                        diff = date12 - date11
                        hour1 = diff.days * 24

                        hours = (diff.seconds) // 3600
                        minutes = ((diff.seconds) % 3600) // 60
                        totalhours = hour1 + hours
                        # task.task_hours =totalhours

                        if myrec.offer_valid == '24hrs':
                            if totalhours > 24:
                                b = True
                                print('lost24')
                        elif myrec.offer_valid == '3days':
                            if totalhours > 72:
                                b = True
                                print('lost72')
                        elif myrec.offer_valid == '1Week':
                            if totalhours > 168:
                                b = True
                                print('lost168')

                        elif myrec.offer_valid == '2Week':
                            if totalhours > 336:  # 336
                                b = True
                                print('lost336')

                        if totalhours > 336:  # 336
                            b = True
                            rec.is_lost_blue = True
                        if  myrec.state == 'cancel':  # 336
                            print("hi cancel")
                            rec.is_lost_green = True
                            rec.stage_id = stage.id
                            rec.write({'stage_id': stage.id,'is_lost_green':True})

                        print(totalhours)
                        print(myrec.state)
                        rec.is_lost = b


                    print(stage.name)
                    for r  in record:
                        print(r.is_lost)
                        if r.is_lost == True:
                            if stage:
                                r.stage_id = stage.id
                                r.write({'stage_id': stage.id})

    @api.multi
    @api.model
    def cron_do_task_crm(self):
        # self.server_do_action()
        self.review_all_lead()

    # @api.depends('is_lost')
    # def change_stages(self):
    #     stage = self.env['crm.stage'].search([('name', '=', 'Lost')])
    #     for record in self:
    #         if record.is_lost ==True:
    #             if stage:
    #                 record.write({'stage_id': stage.id})
    @api.model
    def _get_lead_creation(self):

        return self.env.uid

    lead_user_id = fields.Many2one(comodel_name="res.users" ,string ="Lead Creator", default =_get_lead_creation)

    @api.depends('partner_id')
    def get_type_of_partner_id(self):
        for record in self:
            if record.partner_id.company_type == 'person':
                record.is_company = False
            else:
                record.is_company = True

    @api.onchange('car_type_id')
    def _onchange_car_type_id(self):
        self.is_insured = self.car_type_id.is_insured
        self.claim_number = self.car_type_id.license_plate

    @api.multi
    def get_quotation_order(self):
        sale_id = False
        sale_obj = self.env['sale.order']
        stage = self.env['sales.stages'].search([('name', '=', 'New')])


        for rec in self:
            sale_id = sale_obj.create({
              'partner_id': self.partner_id.id,
              'team_id': self.team_id.id,
              'campaign_id': self.campaign_id.id,
              'medium_id': self.medium_id.id,
              'opportunity_id': self.id,
              'origin': self.name,
              'x_studio_source_2': self.crm_source_id.id,
              'x_studio_field_icWOZ': self.agency_location_id.id,
              'vehicle': self.car_type_id.id,
              'is_insured': self.is_insured,
              'claim_no': self.claim_number,
              'lead_user_id':self.lead_user_id.id,
                'sales_stage':stage.id,
            })

        for line in rec.crm_order_line_ids:
            self.env['sale.order.line'].create({
              'order_id': sale_id.id,
              'product_id': line.product_id.id,
              'product_uom_qty': line.product_uom_qty,
            })
        self.sales_id=sale_id.id
        # sales = self.env['crm.stage'].search([('name','=','sales')])
        # self.write({
        #     'stage_id': sales.id
        # })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotation',
            'res_model': 'sale.order',
            'res_id': sale_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def write(self, vals):

        if self.is_insured == True:
            print("zaki...")
            won = self.env['crm.stage'].search([('name', '=', 'Won')])
            vals['stage_id'] = won.id

        res = super(CrmLead, self).write(vals)
        return res


    @api.multi
    def send_notification_to_logistic(self):
        if self.logistic_user_id.id :
            user_Obj = self.env['res.users'].browse(self.logistic_user_id.id)
            for i in user_Obj:
                act_type_xmlid = 'mail.mail_activity_data_todo'
                date_deadline = datetime.now().strftime('%Y-%m-%d')
                summary = 'New Lead Notification'
                note = 'New Lead is created, Please take follow-up.'

                if act_type_xmlid:
                    activity_type = self.sudo().env.ref(act_type_xmlid)

                model_id = self.env['ir.model']._get(self._name).id

                create_vals = {
                    'activity_type_id': activity_type.id,
                    'summary': summary or activity_type.summary,
                    'automated': True,
                    'note': note,
                    'date_deadline': date_deadline,
                    'res_model_id': model_id,
                    'res_id': self.id,
                    'view_id': self.env.ref('crm.crm_case_form_view_oppor').id,
                    'user_id': i.id,

                }

                activities = self.env['mail.activity'].create(create_vals)
            logistic = self.env['crm.stage'].search([('name','=','logistic')])
            self.write({
                'stage_id': logistic.id
            })
            self.message_post(body='New Opportunity Need Approval',
                                     subtype='mt_comment',
                                     subject='New Opportunity Need Approval',
                                     message_type='comment')


class ResCity(models.Model):
    _name = "res.city"

    name = fields.Char()


class SaleOrderLine(models.Model):
    _name = "crm.lead.order.line"

    crm_lead_id = fields.Many2one(comodel_name="crm.lead")

    product_id = fields.Many2one(comodel_name="product.product")
    name = fields.Char()
    product_uom_qty = fields.Float(string="Quantity")
    product_uom = fields.Many2one(comodel_name="uom.uom", string="Unit of Measure")
    price_unit = fields.Float(string="Unit Price")

class SalesStagesGr(models.Model):
    _name='sales.stages'
    _description = "Sales Stages"
    _rec_name = 'name'
    _order = "sequence, name, id"

    name= fields.Char(string="stage name")
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")


class SalesOrdercrm(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['sales.stages'].search([])
        return stage_ids

    lead_user_id = fields.Many2one(comodel_name="res.users" ,string ="Lead Creator", )
    sales_stage = fields.Many2one(comodel_name="sales.stages" ,string ="Sales stages",group_expand='_read_group_stage_ids')
    sales_user_id = fields.Many2one(comodel_name="res.users", string="Sales Man", )
    user_id = fields.Many2one('res.users', string='CIP', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)
    offer_valid = fields.Selection([
        ('24hrs', '24 Hrs'),
        ('3days', '3 Days'),
        ('1Week', '1 Week'),
        ('2Week', '2 Week'),
    ], 'Validity', default='3days')


    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        # ('sent', 'Sent'),
        ('sign', 'Quotation Signed'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=4, default='draft')

    @api.multi
    def action_reject(self):

        return self.write({'state': 'reject'})

    @api.multi
    def send_notification(self,msummary,mnote):
        if self.sales_user_id:
            user_Obj = self.env['res.users'].browse(self.sales_user_id.id)
            for i in user_Obj:
                act_type_xmlid = 'mail.mail_activity_data_todo'
                date_deadline = datetime.now().strftime('%Y-%m-%d')
                summary = msummary  #'The Quotation is Confirmed'
                note = mnote #'New Quotation Need Follow ' + str(self.sale_order_id.name) + '.'

                if act_type_xmlid:
                    activity_type = self.sudo().env.ref(act_type_xmlid)

                model_id = self.env['ir.model']._get('sale.order').id

                create_vals = {
                    'activity_type_id': activity_type.id,
                    'summary': summary or activity_type.summary,
                    'automated': True,
                    'note': note,
                    'date_deadline': date_deadline,
                    'res_model_id': model_id,
                    'res_id': self.id,
                    'view_id': self.env.ref('sale.view_order_form').id,
                    'user_id': i.id,

                }
                print(create_vals)

            activities = self.env['mail.activity'].sudo().create(create_vals)

            # self.message_post(body='New Quotation Need Follow up',
            #                   subtype='mt_comment',
            #                   subject='New Quotation Need Follow up',
            #                   message_type='comment')
    @api.multi
    def write(self, vals):

        # if self.is_insured == True:
        # #     for rec in self:
        # #         logistic = self.env['crm.stage'].search([('name', '=', 'logistic')])
        # #         rec.opportunity_id.write({
        # #             'stage_id': logistic.id
        # #         })
        # # else  :
        #     for rec in self:
        #         won = self.env['crm.stage'].search([('name', '=', 'Won')])
        #         rec.opportunity_id.write({
        #             'stage_id': won.id
        #         })
        if self.is_insured == True:
            for rec in self:
                won = self.env['crm.stage'].search([('name', '=', 'Won')])
                rec.opportunity_id.write({
                    'stage_id': won.id
                })
        res = super(SalesOrdercrm, self).write(vals)
        return res

    @api.multi
    def action_confirm2(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        return True

    @api.multi
    def action_confirm_replica(self):
        c=0
        print(len(self.order_line))
        for rec in self.order_line:
            if rec.product_id.type == 'product':
                c+=1
        if c== len(self.order_line) :
            self.action_confirm2()
            print(" hi .. iam storable ")
        else:
           if c == 0 :

                # if not self.alloy_digital_signature:
                #     raise UserError(_("You must add Your signature"))
                if self.alloy_digital_signature:
                    super(SalesOrdercrm, self).action_confirm_replica()
                    if self.is_insured == False:
                        for rec in self:
                            won = self.env['crm.stage'].search([('name', '=', 'Won')])
                            rec.opportunity_id.write({
                                'stage_id': won.id
                            })
                    else:
                        for rec in self:
                            won = self.env['crm.stage'].search([('name', '=', 'Won')])
                            rec.opportunity_id.write({
                                'stage_id': won.id
                            })
                    self.send_notification("The Quotation Was confirmed",str(self.name) +"The Quotation Was confirmed"+ '.')
                else:
                    raise UserError(_("You must add Your signature"))
           else:
               raise UserError(_("All Products must be storable products or Services"))
    # @api.multi
    # def action_confirm(self):
    #     if self.alloy_digital_signature:
    #         if self._get_forbidden_state_confirm() & set(self.mapped('state')):
    #             raise UserError(_(
    #                 'It is not allowed to confirm an order in the following states: %s'
    #             ) % (', '.join(self._get_forbidden_state_confirm())))
    #
    #         for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
    #             order.message_subscribe([order.partner_id.id])
    #         self.write({
    #             'state': 'sale',
    #             'confirmation_date': fields.Datetime.now()
    #         })
    #         self._action_confirm()
    #         if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
    #             self.action_done()
    #         return True

    @api.multi
    def action_cancel(self):
        res = super(SalesOrdercrm, self).action_cancel()
        for rec in self:
            lost = self.env['crm.stage'].search([('name', '=', 'Lost')])
            rec.opportunity_id.write({
                'stage_id': lost.id
            })
        return res

    def send_m(self, msubj="", mbody="", recipient_partners=[]):

        if msubj != "":
            msgsubject = msubj

        if mbody != "":
            msgbody = mbody

        print(recipient_partners)

        if len(recipient_partners):
            sale_id = self.env['sale.order'].browse(self._context.get('active_id', False))
            sale_id.message_post(body=msgbody,
                                    subtype='mail.mt_comment',
                                    subject=msgsubject,
                                    partner_ids=recipient_partners,
                                    message_type='comment')
            # comment



    # @api.depends('sales_user_id')
    # def send_notification_to_salesman(self):
    #     print("before????")
    #     if self.sales_user_id:
    #
    #         self.send_notification_to_s()
    #         print("hi ....?????")
    #         # self.send_m("New Quotation for Follow up","New Quotation for Follow up"+str(self.name),user_Obj)

    # @api.multi
    # def action_confirm(self):
    #     if self._get_forbidden_state_confirm() & set(self.mapped('state')):
    #         raise UserError(_(
    #             'It is not allowed to confirm an order in the following states: %s'
    #         ) % (', '.join(self._get_forbidden_state_confirm())))
    #
    #     for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
    #         order.message_subscribe([order.partner_id.id])
    #     self.write({
    #         'state': 'sale',
    #         'confirmation_date': fields.Datetime.now()
    #     })
    #     self._action_confirm()
    #     if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
    #         self.action_done()
    #     return True
    #
    @api.multi
    def action_confirm(self):

        return True

    def send_salesman(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Choose Sales Man',
            'res_model': 'salesman.wizard',
             'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }