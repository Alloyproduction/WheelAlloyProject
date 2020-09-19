# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils

class accountinvoice(models.Model):
    _inherit = "account.invoice"
    amount_tax_signed = fields.Monetary(string='Tax in Invoice Currency', currency_field='currency_id',
                                        readonly=True, compute='_compute_sign_taxes', store=True)
    amount_untaxed_invoice_signed = fields.Monetary(string='Untaxed Amount in Invoice Currency',
                                                    currency_field='currency_id',
                                                    readonly=True, compute='_compute_sign_taxes' , store=True)
    origin_purchase_id = fields.Many2one(comodel_name="purchase.order",string="Source Document Link")
    first_payment_date =fields.Date(string="Payment Date", readonly=True,  related="payment_move_line_ids.date")

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



class PurchaseOrder2(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'type': 'in_invoice',
            'default_purchase_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'company_id': self.company_id.id
        }
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.invoice_supplier_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_origin'] = self.name+ "hi.."
        result['context']['default_reference'] = self.partner_ref
        print(self.id)
        result['context']['default_origin_purchase_id'] = self.id
        return result



class account_payment2(models.Model):

    _inherit = "account.payment"

    # _inherit = ['mail.thread', 'account.abstract.payment']
    def get_recipients(self):
        group = self.env['res.groups'].search(
            [('name', 'in', ['Accountant', '', 'Advisor', 'Billing'])])  # self.env.ref('stock.group_stock_manager')
        print(group)
        recipients = []
        for g in group:
            for recipient in g.users:
                if recipient.partner_id.id not in recipients:
                    recipients.append(recipient.partner_id.id)
                    print(recipient.name)

        return recipients


    def send_m(self, msubj="", mbody=""  , recipient_partners=[]):

        if msubj != "":
            msgsubject = msubj

        if mbody != "":
            msgbody = mbody

        print(recipient_partners)

        if len(recipient_partners):
            invoide_id = self.env['account.invoice'].browse(self._context.get('active_id', False))
            invoide_id.message_post(body=msgbody,
                              subtype='mail.mt_comment',
                              subject=msgsubject,
                              partner_ids=recipient_partners,
                              message_type='comment')
    @api.multi
    def action_validate_invoice_payment(self):
        res =super(account_payment2, self).action_validate_invoice_payment()
        print(self)
        recipients = self.get_recipients()
        print(recipients)
        for x in recipients:
            print(x)

        recipients =[300, 280]
        self.send_m("Bill Paid","This Bill paid",recipients)
        return   res

# class account_prince(models.Model):
#     _name = 'account_prince.account_prince'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100