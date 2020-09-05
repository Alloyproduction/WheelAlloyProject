# -*- coding: utf-8 -*-

from odoo import models, fields, api



class paymentflow(models.Model):
    _inherit = 'account.invoice'
    # _inherit = ['purchase.order','mail.thread']
    @api.multi
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        # template = self.env.ref('account.email_template_edi_invoice', False)
        template = self.env['mail.template'].browse(53)
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', False)
        # have model_description in template language
        lang = self.env.context.get('lang')
        if template and template.lang:
            lang = template._render_template(template.lang, 'account.invoice', self.id)
        self = self.with_context(lang=lang)
        TYPES = {
            'out_invoice': _('Invoice'),
            'in_invoice': _('Vendor Bill'),
            'out_refund': _('Credit Note'),
            'in_refund': _('Vendor Credit note'),
        }
        ctx = dict(
            default_model='account.invoice',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            model_description=TYPES[self.type],
            custom_layout="mail.mail_notification_paynow",
            force_email=True
        )
        return {
            'name': _('Send Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

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

