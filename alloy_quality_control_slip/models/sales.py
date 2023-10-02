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
                    if line.stage_id.name == 'Delivery' or  line.stage_id.name == 'Cancel' or line.stage_id.name == 'Reject' :  # line.stage_id.name == 'Finished and QC' or
                        c+=1
                if(c==len(task_ids)):
                    rec.is_task_Q_delivered = True

class QualityControlSlip(models.Model):
    _name = 'quality.control.slip'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Reference', required=True, copy=False,
                           readonly=True, index=True, default=lambda self: _('New'))
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
    partner_id = fields.Many2one('res.partner', related='sale_id.partner_id')
    company_id = fields.Many2one('res.company')
    alloy_digital_signature = fields.Binary(widget="signature", required=True)
    signer_name = fields.Char(string= "Signer Name", required=True )
    state = fields.Selection(string="state", selection=[('draft', 'Draft'),('accept', 'Accept'), ('deny', 'Deny')],
                             default='draft', track_visibility='always',)
    job_card = fields.Char()
    type_name = fields.Char('Type Name', compute='_compute_type_name')

    @api.multi
    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            record.type_name = _('Quotation') if record.state in ('draft', 'accept', 'deny') else _('Quality Control')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('quality.control.slip') or _('New')
        result = super(QualityControlSlip, self).create(vals)
        return result

    @api.multi
    def accept_qc_slip(self):
        for rec in self:
            rec.sale_id.alloy_digital_signature = rec.alloy_digital_signature
            rec.confirmation_date = fields.date.today()
            rec.state = 'accept'

            for rec in self.sale_id:
                task_ids = self.env['project.task'].search([('sale', '=', rec.id)])
                if task_ids and self.state == 'accept':
                    for line in task_ids:
                        if line.stage_id.name == 'Delivery':  # line.stage_id.name == 'Finished and QC' or
                            line.is_delete_stage = True

    @api.multi
    def deny_qc_slip(self):
        for rec in self:
            rec.confirmation_date = fields.date.today()
            rec.state = 'deny'

    @api.multi
    def set_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def action_send_qc(self):

        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('alloy_quality_control_slip', 'qc_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'quality.control.slip', self.ids[0])
        ctx = {
            'default_model': 'quality.control.slip',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'model_description': self.with_context(lang=lang).type_name,
            'custom_layout': "mail.mail_notification_borders",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

        # template_id = self.env.ref('alloy_quality_control_slip.qc_email_template').id
        # template = self.env['mail.template'].browse(template_id)
        # template.send_mail(self.id, force_send=True)
        #
        # print("Sending email")
        # self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)





    # @api.multi
    # @api.depends('state')
    # def _change_is_delete_stage(self):
    #    print("reach ....before .. ")
    #    for rec in self.sale_id:
    #         task_ids = self.env['project.task'].search([('sale', '=', rec.id)])
    #         if task_ids and self.state == 'accept':
    #             for line in task_ids:
    #                 if line.stage_id.name == 'Delivery':  # line.stage_id.name == 'Finished and QC' or
    #                      line.is_delete_stage = True
    #                      print("reach ...... ")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_qc_created = fields.Boolean('Is Qc Created', default=False)
    qc_slip_id = fields.Many2one(comodel_name="quality.control.slip")

    def qc_mail_reminder(self):
        """Sending Email notification to make invoice to the sale order"""
        print('......')
        so_inv_created = self.env['sale.order'].search([('is_qc_created','=' ,True),('qc_slip_id','!=' ,False)], limit=500)
        print(so_inv_created)

        for i in so_inv_created:
            print(so_inv_created)
            print(i.is_qc_created)
            if i.invoice_ids:
                print('worked22')
                i.is_qc_created = False
            else:
                groups = self.env['res.groups'].search([('name', '=', "QC invoice reminder")])
                recipient_partners = []
                print(groups)
                for group in groups:
                    for recipient in group.users:
                        if recipient.partner_id.id not in recipient_partners:
                            recipient_partners.append(recipient.partner_id.id)
                            print(recipient.login)
                            print(recipient_partners)

                msg_sub = "QualityControl Without Invoice"
                msg_body = "Please Create Invoice To This Sale Order. " + i.name
                print(recipient_partners)
                print('wanted1 still')
                if len(recipient_partners):
                    print('worked33 and sent')
                    i.sudo().message_post(body=msg_body,
                                      subtype='mt_comment',
                                      subject=msg_sub,
                                      partner_ids=recipient_partners,
                                      message_type='comment')

                i.is_qc_created = False



    @api.multi
    def make_quality_control_slip(self):


        # qc_search_obj2 = self.search([('invoice_ids', '=', False),('qc_slip_id', '!=', False)])
        if not self.invoice_ids.number:
            self.is_qc_created = True

        total_qty = 0.0
        qc_obj = self.env['quality.control.slip']
        for rec in self:
            qc_search_obj = qc_obj.search([('id','=',self.qc_slip_id.id)])
            print("Reference")
            print(qc_search_obj.name)
            if qc_search_obj:
                print("done1")
                for line in rec.order_line:
                    total_qty += line.product_uom_qty
                print("kk",total_qty)
                qc_search_obj.update({
                    'invoice_number': rec.invoice_ids.number,
                    'claim_no': rec.claim_no,
                    'license_plate': rec.vehicle.license_plate,
                    'confirmation_date': str(rec.confirmation_date),
                    'no_of_pieces': total_qty,
                    'insurance_company': rec.vehicle.insurance_company.id,
                    'agency_name': rec.x_studio_field_icWOZ.id,
                    'job_card': rec.x_studio_agency_job_card,
                    'vehicle': rec.vehicle.id,
                    'sale_id': rec.id,
                    # 'service_advisor': rec.service_advisor.id,
                    'user_id': rec.user_id.id,
                })

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
                print("done2")
                total_qty=0
                for line in rec.order_line:
                    total_qty += line.product_uom_qty

                print("Reference")
                print(qc_search_obj.name)
                qc_id = qc_obj.create({
                  'invoice_number': rec.invoice_ids.number,
                  'claim_no': rec.claim_no,
                  'license_plate': rec.vehicle.license_plate,
                  'confirmation_date': rec.confirmation_date,
                  'no_of_pieces': total_qty,
                  'insurance_company': rec.vehicle.insurance_company.id,
                  'agency_name': rec.x_studio_field_icWOZ.id,
                  'job_card': rec.x_studio_agency_job_card,
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
