# -*- coding: utf-8 -*-

from odoo import models, api,_


class SprogrouppurcaseRequest(models.Model):
    _inherit = "sprogroup.purchase.request"

    @api.multi
    def button_to_approve(self):
        res = super(SprogrouppurcaseRequest, self).button_to_approve()
        for rec in self:
            groups = self.env['res.groups'].search([('name', '=', 'Sprogroup Purchase Request Manager')])
            recipient_partners = []
            for group in groups:
                for recipient in group.users:
                    if recipient.partner_id.id not in recipient_partners:
                        recipient_partners.append(recipient.partner_id.id)
            if len(recipient_partners):
                rec.message_post(body='New purchase request require your approval',
                                 subtype='mt_comment',
                                 subject='Approve Purchase Request',
                                 partner_ids=recipient_partners,
                                 message_type='comment')
        return res