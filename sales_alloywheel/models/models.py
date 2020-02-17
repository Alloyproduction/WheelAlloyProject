# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    source = fields.Char(compute="get_source_value")

    @api.depends('origin')
    def get_source_value(self):
        if self.origin:
            sale_id = self.env['sale.order'].search([('name', '=', self.origin)])
            if sale_id:
                self.source = sale_id.source


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    source = fields.Char()
    is_person = fields.Boolean(compute="get_source_type")

    @api.depends('partner_id')
    def get_source_type(self):
        if self.partner_id:
            for record in self:
                if record.partner_id.company_type == 'person':
                    record.is_person = True
                else:
                    record.is_person = False


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    minimum_qtys = fields.Float(string="Minimum Quantity")

    @api.multi
    def server_do_action(self):
        product_template_ids = self.search([])
        for record in product_template_ids:
            if record.qty_available <= record.minimum_qtys:
                groups = self.env['res.groups'].search([('name', '=', 'ceo')])
                recipient_partners = []
                for group in groups:
                    for recipient in group.users:
                        if recipient.partner_id.id not in recipient_partners:
                            recipient_partners.append(recipient.partner_id.id)
                if len(recipient_partners):
                    record.message_post(body='There is No enough QTY',
                                        subtype='mt_comment',
                                        subject='Minimum Qty',
                                        partner_ids=recipient_partners,
                                        message_type='notification')


    @api.model
    def cron_do_task(self):
        # self.server_do_action()
        self.send_low_stock_via_email()

    @api.multi
    def send_low_stock_via_email(self):
        header_label_list = ["Internal Refrence", "Name", "Qty On Hand", "Low Stock Qty"]
        product_obj = self.env['product.product']
        product_ids = product_obj.search([])
        product_ids = product_ids.filtered(lambda r: r.qty_available <= r.minimum_qty and r.minimum_qty >= 0)
        print('sdjfhssdf', product_ids)
        group =  self.env['res.groups'].search([('name', '=', 'ceo')])  #self.env.ref('stock.group_stock_manager')
        print(group)
        recipients = []
        for recipient in group.users:
            recipients.append((4, recipient.partner_id.id))
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
            body += """ 
                <tr style="font-size:14px; border: 1px solid black">
                    <td style="text-align:center; border: 1px solid black">%s</td>
                    <td style="text-align:center; border: 1px solid black">%s</td>
                    <td style="text-align:center; border: 1px solid black">%s</td>
                    <td style="text-align:center; border: 1px solid black">%s</td>
                </tr>
                """ % (product_ids.default_code, product_ids.name, product_ids.qty_available, product_ids.minimum_qty)
            "</table>"
        post_vars = {'subject': "Low stock notification",
                     'body': body,
                     'partner_ids': recipients, }
        self.message_post(
            type="notification",
            subtype="mt_comment",
            **post_vars)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    current_user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    @api.onchange('current_user_id')
    def get_current_access_partner(self):
        """"get current access partner related to current user"""
        self.partner_id = self.current_user_id.partner_id
