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
        self.server_do_action()


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    current_user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    @api.onchange('current_user_id')
    def get_current_access_partner(self):
        """"get current access partner related to current user"""
        self.partner_id = self.current_user_id.partner_id
