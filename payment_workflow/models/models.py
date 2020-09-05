# -*- coding: utf-8 -*-

from odoo import models, fields, api



class paymentflow(models.Model):
    _inherit = 'sale.order'
    # _inherit = ['purchase.order','mail.thread']

    #
    # is_manager = fields.Boolean(string="Manager Approval")
    # is_leader = fields.Boolean(string="Leader Approval")
    # is_ceo = fields.Boolean(string="CEO Approval")
    # state_approve = fields.Selection([
    #     ('NotApprove', "NotApprove"),
    #     ('Leader', "Leader"),
    #     ('Manager', "Manager"),
    #     ('CEO', "CEO"),
    # ], default='NotApprove')
    #
    # @api.multi
    # def action_Leader(self):
    #     self.is_leader = True
    #     self.state_approve = 'Leader'
    #     self.send_m("payment approvel " + self.name, "Approved By Leader ( " + self.env.user.name + ")")
    #
    # @api.multi
    # def action_Manager(self):
    #     self.is_manager = True
    #     self.state_approve = 'Manager'
    #     self.send_m("payment approvel " + self.name, "Approved By Maneger ( " + self.env.user.name + ")")
    #
    #     @api.multi
    #     def action_CEO(self):
    #         self.is_ceo = True
    #         self.state_approve = 'CEO'
    #         self.send_m("payment approvel " + self.name, "Approved By CEO ( " + self.env.user.name + ")")

