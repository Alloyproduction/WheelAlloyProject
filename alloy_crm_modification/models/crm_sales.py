# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_order_line_ids = fields.One2many(comodel_name="crm.lead.order.line", inverse_name="crm_lead_id", string="order lines")
    logistic_user_id = fields.Many2one(comodel_name="res.users")
    agency_location_id = fields.Many2one(comodel_name="generic.location")
    car_type_id = fields.Many2one(comodel_name="vehicle")
    is_insured = fields.Boolean(string="insured")
    is_company = fields.Boolean(compute='get_type_of_partner_id')
    claim_number = fields.Char(string="Claim #")
    crm_source_id = fields.Many2one(comodel_name="sale.order.source", string="source",)
    city_id = fields.Many2one('res.city', 'City')

    @api.depends('partner_id')
    def get_type_of_partner_id(self):
        for record in self:
            if record.partner_id.company_type == 'person':
                record.is_company = False
            else:
                record.is_company = True

    @api.onchange('car_type_id')
    def _onchange_car_type_id(self):
        self.is_insured = self.car_type_id.is_insured
        self.claim_number = self.car_type_id.license_plate

    @api.multi
    def get_quotation_order(self):
        sale_id = False
        sale_obj = self.env['sale.order']
        for rec in self:
            sale_id = sale_obj.create({
              'partner_id': self.partner_id.id,
              'team_id': self.team_id.id,
              'campaign_id': self.campaign_id.id,
              'medium_id': self.medium_id.id,
              'opportunity_id': self.id,
              'origin': self.name,
              'x_studio_source_2': self.crm_source_id.id,
              'x_studio_field_icWOZ': self.agency_location_id.id,
              'vehicle': self.car_type_id.id,
              'is_insured': self.is_insured,
              'claim_no': self.claim_number,
            })

        for line in rec.crm_order_line_ids:
            self.env['sale.order.line'].create({
              'order_id': sale_id.id,
              'product_id': line.product_id.id,
              'product_uom_qty': line.product_uom_qty,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotation',
            'res_model': 'sale.order',
            'res_id': sale_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def send_notification_to_logistic(self):
        user_Obj = self.env['res.users'].browse(self.logistic_user_id.id)
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
                'view_id': self.env.ref('crm.crm_case_form_view_oppor').id,
                'user_id': i.id,

            }

            activities = self.env['mail.activity'].create(create_vals)

        self.message_post(body='New Opportunity Need Approval',
                                 subtype='mt_comment',
                                 subject='New Opportunity Need Approval',
                                 message_type='comment')


class ResCity(models.Model):
    _name = "res.city"

    name = fields.Char()


class SaleOrderLine(models.Model):
    _name = "crm.lead.order.line"

    crm_lead_id = fields.Many2one(comodel_name="crm.lead")

    product_id = fields.Many2one(comodel_name="product.product")
    name = fields.Char()
    product_uom_qty = fields.Float(string="Quantity")
    product_uom = fields.Many2one(comodel_name="uom.uom", string="Unit of Measure")
    price_unit = fields.Float(string="Unit Price")