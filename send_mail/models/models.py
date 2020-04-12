# -*- coding: utf-8 -*-

from odoo import models, fields, api

class send_mail(models.Model):
    _name = 'alloy.send'
    _inherit = 'mail.thread'

    @api.model
    def cron_do_task(self):
        # self.server_do_action()
        self.send_low_stock_via_email()\

    @api.model
    def cron_do_task_outgoing(self):
        # self.server_do_action()
        self.send_all_outgoing()

    @api.multi
    def send_low_stock_via_email(self):
        # mymail =self.env['mail.thread']
        header_label_list = ["Internal Refrence", "Name", "Qty On Hand", "Low Stock Qty"]
        product_obj = self.env['product.template']
        product_ids = product_obj.search([])
        product_ids = product_ids.filtered(lambda r: r.qty_available <= r.minimum_qty and r.minimum_qty >= 0)
        print('sdjfhssdf', product_ids)
        group = self.env['res.groups'].search([('name', '=', 'ceo')])  # self.env.ref('stock.group_stock_manager')
        print(group)
        recipients = []
        for recipient in group.users:
            if recipient.partner_id.id not in recipients:
                recipients.append(recipient.partner_id.id)

        # Notification message body
        body = """  
            <table class="table table-bordered">
                <tr style="font-size:14px; border: 1px solid black">
                    <th style="text-align:center; border: 1px solid black">%s</th>
                    <th style="text-align:center; border: 1px solid black">%s</th>
                    <th style="text-align:center; border: 1px solid black">%s</th>
                    <th style="text-align:center; border: 1px solid black">%s</th>
                    </tr>
                 """ % (header_label_list[0], header_label_list[1], header_label_list[2], header_label_list[3])
        for product_ids in product_ids:
            if product_ids.minimum_qty:
                body += """ 
                        <tr style="font-size:14px; border: 1px solid black">
                            <td style="text-align:center; border: 1px solid black">%s</td>
                            <td style="text-align:center; border: 1px solid black">%s</td>
                            <td style="text-align:center; border: 1px solid black">%s</td>
                            <td style="text-align:center; border: 1px solid black">%s</td>
                        </tr>
                        """ % (
                product_ids.default_code, product_ids.name, product_ids.qty_available, product_ids.minimum_qty)
                "</table>"

        post_vars = {'subject': "Low stock notification",
                     'body': body,
                     'partner_ids': recipients, }
        # print(body)
        # self.message_post(
        #     type="notification",
        #     subtype="mail.mt_comment",
        #     message_type='comment'
        #     **post_vars)
        adminuser = self.env['res.users'].search([('name', '=', 'Administrator')])

        if len(recipients):
            self.message_post(body=body,
                              subtype='mail.mt_comment',
                              subject="Low stock notification",
                              partner_ids=recipients,
                              message_type='comment',
                              author_id=adminuser.partner_id.id)

    @api.multi
    def send_all_outgoing(self):

        msg_ids = self.env['mail.mail'].search([('state', '=', 'outgoing')])  # self.env.ref('stock.group_stock_manager')
        for msg in msg_ids:
            msg.send()



#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100