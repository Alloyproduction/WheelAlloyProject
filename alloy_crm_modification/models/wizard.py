from odoo import models, fields, api, _
from datetime import datetime

class Wizard(models.TransientModel):
    _name = 'salesman.wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = "Salesman for Sales Order Quotation "

    def _default_sales(self):
        return self.env['sale.order'].browse(self._context.get('active_id'))

    sale_order_id = fields.Many2one('sale.order',   string="Sales", required=True ,default=_default_sales)
    sales_id = fields.Many2one('res.users', string="Sales Man")

    @api.multi
    def send_notification_to_s(self):
        if self.sales_id:
            user_Obj = self.env['res.users'].browse(self.sales_id.id)
            for i in user_Obj:
                act_type_xmlid = 'mail.mail_activity_data_todo'
                date_deadline = datetime.now().strftime('%Y-%m-%d')
                summary = 'New Quotation Need Follow up'
                note = 'New Quotation Need Follow ' + str(self.sale_order_id.name) + '.'

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
                    'res_id': self.sale_order_id.id,
                    'view_id': self.env.ref('sale.view_order_form').id,
                    'user_id': i.id,

                }
                print(create_vals)

            activities = self.env['mail.activity'].sudo().create(create_vals)

            # self.message_post(body='New Quotation Need Follow up',
            #                   subtype='mt_comment',
            #                   subject='New Quotation Need Follow up',
            #                   message_type='comment')

    def send_m(self, msubj="", mbody="", recipient_partners=[]):

        if msubj != "":
            msgsubject = msubj

        if mbody != "":
            msgbody = mbody

        print(recipient_partners)

        if len(recipient_partners):

            self.sale_order_id.message_post(body=msgbody,
                                 subtype='mail.mt_comment',
                                 subject=msgsubject,
                                 partner_ids=recipient_partners,
                                 message_type='comment')
    @api.multi
    def choose(self):
        if self.sales_id :
            self.sale_order_id.sales_user_id  = self.sales_id.id

            self.sudo().sale_order_id.write({'sales_user_id' :self.sales_id.id})
            # res.write({'sales_user_id' :self.sales_id.id})
            # recipient_partners = []
            # recipient_partners.append(self.sales_id.partner_id.id)
            # self.send_m("New Quotation Need for Follow up ","New Quotation Need for Follow up "+str(self.sale_order_id.name),recipient_partners)
            self.send_notification_to_s()
            return {}
