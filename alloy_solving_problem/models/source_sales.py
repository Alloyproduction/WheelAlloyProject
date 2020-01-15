# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class ResUsers(models.Model):
    _inherit = "res.users"

    is_receive_crm_notification = fields.Boolean(string="receive crm notification",  )


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, values):
        company = super(CrmLead, self).create(values)
        company._create_function()
        return company


    @api.multi
    def _create_function(self):
        user_Obj = self.env['res.users'].search([('is_receive_crm_notification', '=', True)])
        for i in user_Obj:
            act_type_xmlid = 'mail.mail_activity_data_todo'
            date_deadline = datetime.now().strftime('%Y-%m-%d')
            summary = 'New Lead Notification'
            note = 'New Lead is created, Please take follow-up.'

            if act_type_xmlid:
                activity_type = self.sudo().env.ref(act_type_xmlid)

            model_id = self.env['ir.model']._get(self._name).id

            create_vals = {
                'activity_type_id': activity_type.id,
                'summary': summary or activity_type.summary,
                'automated': True,
                'note': note,
                'date_deadline': date_deadline,
                'res_model_id': model_id,
                'res_id': self.id,
                'user_id': i.id,

            }

            activities = self.env['mail.activity'].create(create_vals)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount_fixed = fields.Float()


class PurchaseOrderLinee(models.Model):
    _inherit = "res.partner"

    customer_code = fields.Char()

    @api.depends('is_company', 'name', 'customer_code', 'parent_id.name', 'type', 'company_name')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None, html_format=None, show_vat=False)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    @api.multi
    @api.depends('name', 'customer_code')
    def name_get(self):
        res = []
        for record in self:
            # name = record.name
            name = record.name + str(record.customer_code)
            res.append((record.id, name))
        return res
