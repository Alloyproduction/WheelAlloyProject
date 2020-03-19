# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo import tools


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    # _inherit = ['purchase.order','mail.thread']

    need_CEO_Approve =fields.Boolean(string="Need CEO Approve ",default=True)
    state_approve = fields.Selection([
        ('NotApprove', "NotApprove"),
        ('Leader', "Leader"),
        ('Manager', "Manager"),
        ('CEO', "CEO"),
    ], default='NotApprove')



    is_manager = fields.Boolean(string="Manager Approval")
    is_leader = fields.Boolean(string="Leader Approval")
    is_ceo = fields.Boolean(string="CEO Approval")
    maximum_amount = fields.Float(string="maximum amount")


    @api.multi
    def action_Leader(self):
        self.is_leader = True
        self.state_approve = 'Leader'
        # post_vars = {'subject': "Message subject", 'body': "Approved By Leader" }
        # self.message_post(type="notification", subtype="mt_comment",context=self._context, **post_vars)
        self.send_m("Purchase Order "+self.name,"Approved By Leader ( "+self.env.user.name+")")


    @api.multi
    def action_Manager(self):
        self.is_leader = True
        self.is_manager = True
        self.state_approve = 'Manager'
        # post_vars = {'subject': "Message subject", 'body': "Approved By Manager"}
        # self.message_post(type="notification", subtype="mt_comment", context=self._context, **post_vars)
        self.send_m("Purchase Order " + self.name, "Approved By Manager ( "+self.env.user.name+")")

    @api.multi
    def action_CEO(self):
        self.is_leader = True
        self.is_manager = True
        self.is_ceo = True
        self.state_approve = 'CEO'
        # post_vars = {'subject': "Message subject", 'body': "Approved By CEO"}
        # self.message_post(type="notification", subtype="mt_comment", context=self._context, **post_vars)
        self.send_m("Purchase Order "+self.name,"Approved By CEO ( "+self.env.user.name+")")

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
                all_data ['recipient_partners'].append(299) #ibrahim parner_id

        else:
            all_data ['recipient_partners'].append(self.Approver_leader_id.partner_id.id)
            all_data ['recipient_partners'].append(299)  # ibrahim parner_id
            all_data ['recipient_partners'].append(298)  # Prince parner_id

        print(all_data)
        return all_data

    @api.multi
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

        # if self.assigned_to.partner_id.id and self.assigned_to.partner_id.id not in recipient_partners:
        #     recipient_partners.append(self.assigned_to.partner_id.id)
        # if self.requested_by.partner_id.id and self.requested_by.partner_id.id not in recipient_partners:
        #     recipient_partners.append(self.requested_by.partner_id.id)
        # # recipient_partners.append(4424)

        # if self.employee_name.id and self.employee_name.id not in recipient_partners:
        #             recipient_partners.append(self.employee_name.work_email)

        print(recipient_partners)
        print(self.name)
        # if len(recipient_partners)  :
        #     self.env['mail.mail'].send({'body':msgbody,
        #                       'subtype':'mail.mt_comment',
        #                       'subject':msgsubject,
        #                       'partner_ids':recipient_partners,
        # #                       'message_type':'comment'})
        if len(recipient_partners) :
        #
        #     # author_id = self.env['mail.message']._get_default_author().id
        #
            # self.env['send.purchase.order'].send_mail_msg(msgsubject,msgbody,recipient_partners)
            # print(" hI. Sending")
            self.message_post(body=msgbody,
                              subtype='mail.mt_comment',
                              subject=msgsubject,
                              partner_ids=recipient_partners,
                              message_type='comment')
            # print(x)
            # print("Sending Email")
            # template_id = self.env.ref('alloy_purchase_order_approval.purchase_remind_email').id
            # template_obj = self.env['mail.template'].browse(template_id)
            # template_obj.send_mail(self.id, force_send=True)

        # print("Sending Email")
        # template_id = self.env.ref('alloy_purchase_order_approval.purchase_remind_email').id
        # template_obj = self.env['mail.template'].browse(template_id)
        # template_obj.send_mail(self.id,force_send=True)

        # template_obj = self.env['mail.mail']
        # template_data = {
        #     'subject': 'Due Invoice Notification : ' + str(datetime.now()),
        #     'body_html': 'Hello Yabash',
        #     'email_from': 'hassan',
        #     'email_to': 'elsayedh@hotmail.com',
        #    'model': 'purchase.order'
        #
        # }
        # print(template_data)
        # template_id = template_obj.create(template_data)
        # # template_id.send()
        # template_obj.send(template_id)

    @api.model
    def create(self, values):
        """Override default Odoo create function and extend."""
        # Do your custom logic here
        ctx = dict(self.env.context)
        print("hi context approval module ", ctx)
        # ctx.pop('default_product_id', None)
        # # self = self.with_context(ctx)
        # print("hi context ",ctx)
        # print(self.env.user.id)
        if values.get('name', 'New') == 'New':
            values['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
        res = super(PurchaseOrder, self).create(values)
        print(res)
        # x = self.env['purchase.order'].search([('id', '=',res.id)])
        # print("hi x. ..")
        # print(x.name)

        if res.state_approve and res.state_approve == 'NotApprove':
            print(" if hi")
            post_vars = {'subject': "Purchase Order Created ", 'body': "Required Approve from you...!"}
            res.message_post( message_type='comment', subtype="mt_comment", context=self._context, **post_vars)
            # res.send_m()
            # res.send_m("Purchase Order Created" + res.name, "Required Approve from you... ")
        # else:
        #     print(" else if hi")
        #     res.send_m()

        return res

    # @api.multi
    # def write(self, values):
    #     print(" before if"+ self.state)
    #     if self.state == 'draft':
    #         print(" hi draft stat")
    #         self.send_m()
    #
    #     return super(PurchaseOrder, self).write(values)

    @api.multi
    def manager_approve(self):
        for record in self:

            record.is_manager = True

    @api.multi
    def leader_approve(self):
        for record in self:
            record.is_leader = True

    @api.multi
    def ceo_approve(self):
        for record in self:

            record.is_ceo = True

    @api.multi
    def button_draft(self):
        res = super(PurchaseOrder, self).button_draft()
        for record in self:
            record.write({
                'is_manager': False,
                'is_leader': False,
                'is_ceo': False,
            })
        return res

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        res_conf = self.env['res.config.settings'].sudo()

        max_manager = res_conf.get_values()
        # print(max_manager['maximum_amount_leader'])
        # print(max_manager['maximum_amount'])
        # print(self.amount_total)
        for record in self:
            if record.need_CEO_Approve != True  and  max_manager['maximum_amount'] > self.amount_total :
                if  record.is_leader and  max_manager['maximum_amount_leader'] >  self.amount_total:
                    return res
                else:
                    if not record.is_leader:
                        raise UserError(_("Leader Approval is needed"))

                if  record.is_manager and  max_manager['maximum_amount'] >  self.amount_total:
                    return res
                else:
                    if not record.is_manager:
                         raise UserError(_("Manager Approval is needed"))

            else:


                if record.need_CEO_Approve == True and record.is_ceo == False  :
                   raise UserError(_("CEO Approval is needed"))
                else:
                    return res


class SPurchaseOrder(models.Model):
    # _inherit = "sprogroup.purchase.request"
    _name = 'send.purchase.order'
    _description = 'Send Purchase Order'
    _inherit = ['mail.thread']

    def send_mail_msg(self,msgsubject,msgbody,recipient_partners):
        self.message_post(body=msgbody,
                              subtype='mt_comment',
                              subject=msgsubject,
                              partner_ids=recipient_partners,
                              message_type='comment',
                             )
        # print(x)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_need_approval = fields.Boolean(string="Need Approval")

class Company(models.Model):
    _inherit = 'res.company'


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'


    maximum_amount = fields.Float(string="Amount For Manager"  )
    maximum_amount_leader = fields.Float(string="Amount For Leader"   )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config = self.env['ir.config_parameter'].sudo()
        am_leader=float(config.get_param('maximum_amount_leader'))
        am_manager=float(config.get_param('maximum_amount'))
        res.update(
            maximum_amount_leader=am_leader,
            maximum_amount=am_manager
        )
        return res

    @api.multi
    def set_values(self):
        res=super(ResConfigSettings, self).set_values()
        config = self.env['ir.config_parameter'].sudo()
        config.set_param('maximum_amount_leader',self.maximum_amount_leader)
        config.set_param('maximum_amount', self.maximum_amount)
        # self.write({'maximum_amount_leader':self.maximum_amount_leader,'maximum_amount': self.maximum_amount})
        return res



