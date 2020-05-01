# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class InheritDeSale(models.Model):
    _inherit = 'sale.order'


    is_task_Q_delivered = fields.Boolean(compute='get_delivered_Q_task', default=False)



    def get_delivered_Q_task(self):
        c=0
        for rec in self:
            task_ids = self.env['project.task'].search([('sale', '=', rec.id)])
            if task_ids:
                for line in task_ids:
                    if line.stage_id.name == 'Delivery':  # line.stage_id.name == 'Finished and QC' or
                        c+=1
                if(c==len(task_ids)):
                    rec.is_task_Q_delivered = True

class QualityControlSlip(models.Model):
    _name = 'quality.control.slip'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    invoice_number = fields.Char()
    claim_no = fields.Char()
    license_plate = fields.Char()
    confirmation_date = fields.Date(track_visibility='always',)
    no_of_pieces = fields.Float()
    insurance_company = fields.Many2one('res.partner',string='Insurance Company')
    agency_name = fields.Many2one('generic.location',string='Agency Name')
    vehicle = fields.Many2one('vehicle',string='Car Type')
    service_advisor = fields.Many2one('res.users')
    user_id = fields.Many2one('res.users', track_visibility='always',)
    sale_id = fields.Many2one('sale.order')
    alloy_digital_signature = fields.Binary(widget="signature")
    state = fields.Selection(string="state", selection=[('draft', 'Draft'),('accept', 'Accept'), ('deny', 'Deny')],
                             default='draft', track_visibility='always',)

    @api.multi
    def accept_qc_slip(self):
        for rec in self:
            rec.sale_id.alloy_digital_signature = rec.alloy_digital_signature
            rec.confirmation_date = fields.date.today()
            rec.state = 'accept'

    @api.multi
    def deny_qc_slip(self):
        for rec in self:
            rec.confirmation_date = fields.date.today()
            rec.state = 'deny'

    @api.multi
    def set_to_draft(self):
        for rec in self:
            rec.state = 'draft'



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    qc_slip_id = fields.Many2one(comodel_name="quality.control.slip")

    @api.multi
    def make_quality_control_slip(self):
        total_qty = 0.0
        qc_obj = self.env['quality.control.slip']
        for rec in self:
            qc_search_obj = qc_obj.search([('id','=',self.qc_slip_id.id)])
            if qc_search_obj:
               return {
                'type': 'ir.actions.act_window',
                'name': 'Quality Control Slip',
                'res_model': 'quality.control.slip',
                'res_id': qc_search_obj.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'self',
            }
            else:
                for line in rec.order_line:
                    total_qty += line.product_uom_qty
                qc_id = qc_obj.create({
                  'name': rec.name,
                  'invoice_number': rec.name,
                  'claim_no': rec.claim_no,
                  'license_plate': rec.vehicle.license_plate,
                  'confirmation_date': rec.confirmation_date,
                  'no_of_pieces': total_qty,
                  'insurance_company': rec.vehicle.insurance_company.id,
                  'agency_name': rec.x_studio_field_icWOZ.id,
                  'vehicle': rec.vehicle.id,
                  'sale_id': rec.id,
                  # 'service_advisor': rec.service_advisor.id,
                  'user_id': rec.user_id.id,
                })
                self.qc_slip_id = qc_id.id
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Quality Control Slip',
                    'res_model': 'quality.control.slip',
                    'res_id': qc_id.id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'self',
                }
