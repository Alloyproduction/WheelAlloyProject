# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_manager = fields.Boolean(string="Manager Approval")
    is_leader = fields.Boolean(string="Leader Approval")
    is_ceo = fields.Boolean(string="CEO Approval")
    maximum_amount = fields.Float(string="maximum amount")


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
        for record in self:
            if record.partner_id.is_need_approval:
                if not record.is_manager:
                   raise UserError(_("Manager Approval is needed"))
                if not record.is_leader:
                   raise UserError(_("Leader Approval is needed"))
                if record.is_ceo == False and record.amount_total > record.maximum_amount:
                   raise UserError(_("CEO Approval is needed"))
            else:
                return res

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_need_approval = fields.Boolean(string="Need Approval")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    default_maximum_amount = fields.Float(string="maximum amount",default_model="purchase.order" )
