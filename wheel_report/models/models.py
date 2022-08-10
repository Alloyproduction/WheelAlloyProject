# -*- coding: utf-8 -*-

from odoo import models, fields, api

class wheel_report_2(models.Model):
    _name = 'wheel_report.wheel_report'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char(string='Reference', required=True, copy=False,
                           readonly=True, index=True, default=lambda self: ('New'))
    note = fields.Text()
    partner_id = fields.Many2one('res.partner', 'Partner')
    user_id = fields.Many2one('res.users', 'User')
    so_num = fields.Many2one('sale.order')
    vehicle_name = fields.Char(string = 'Vehicle Name')
    plate_num = fields.Char(string='Plate Number')
    job_card = fields.Char(string='Job Card')
    claim_num = fields.Char(string='Claim Number')
    agency_name = fields.Many2one('generic.location',string='Agency Name')
    advisor_name = fields.Many2one('res.partner', string = 'Service Advisor')
    line_ids = fields.One2many('wheel.report.line', 'request_id',
                               'Wheel Report Line',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')


    @api.model
    def create(self, vals):
        if vals.get('name', ('New')) == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.wheel.check') or ('New')
        result = super(wheel_report_2, self).create(vals)
        return result



    @api.multi
    def action_send_email(self):
        '''
                This function opens a window to compose an email, with the edi sale template message loaded by default
                '''

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('wheel_report', 'alloy_wheel_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'wheel_report.wheel_report', self.ids[0])
        ctx = {
            'default_model': 'wheel_report.wheel_report',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
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



class wheel_report(models.Model):
    _name = 'wheel.report.line'

    product_id = fields.Many2one('product.product', 'Product', required=True, track_visibility='onchange')
    request_id = fields.Many2one('wheel_report.wheel_report', ondelete='cascade', readonly=True)
    tire_status  = fields.Many2many('tire.status.line', track_visibility='onchange')
    air_leaking = fields.Many2many('air.leaking.line', track_visibility='onchange')
    tire = fields.Boolean ()
    rim_status = fields.Many2many('rim.status.line', track_visibility='onchange')
    spoke = fields.Many2many('spoke.line', track_visibility='onchange')
    barrel = fields.Many2many('barrel.line', track_visibility='onchange')
    sensor = fields.Many2many('sensor.line', track_visibility='onchange')
    rim_finished = fields.Boolean("Finished")
    reject = fields.Boolean ("Reject")


    class wheel_tire_status(models.Model):
        _name = 'tire.status.line'

        name = fields.Char()

    class wheel_air_leaking(models.Model):
        _name = 'air.leaking.line'

        name = fields.Char()


    class wheel_rim_status(models.Model):
        _name = 'rim.status.line'

        name = fields.Char()


    class wheel_spoke(models.Model):
        _name = 'spoke.line'

        name = fields.Char()


    class wheel_barrel(models.Model):
        _name = 'barrel.line'

        name = fields.Char()


    class wheel_sensor(models.Model):
        _name = 'sensor.line'

        name = fields.Char()

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    wheel_check_id = fields.Many2one(comodel_name="wheel_report.wheel_report")
    crm_order_line_ids = fields.Many2one(comodel_name="wheel.report.line", string="order lines")


    @api.multi
    def create_wheel_check(self):

        qc_search_obj2 = self.search([('wheel_check_id', '!=', False)])
        # if not self.invoice_ids.number:
        self.is_qc_created = True

        order_line = []
        for line in self.order_line:
            for r in line.product_id:
                product_line = (0, 0, {'product_id': line.product_id.id,})
                order_line.append(product_line)

        qc_obj = self.env['wheel_report.wheel_report']
        for rec in self:
            qc_search_obj = qc_obj.search([('id', '=', self.wheel_check_id.id)])
            # print("Reference")
            # print(qc_search_obj.name)
            if qc_search_obj:
                print("done1")
                qc_search_obj.update({
                    'plate_num': rec.vehicle.license_plate,
                    'job_card': rec.x_studio_agency_job_card,
                    'claim_num': rec.claim_no,
                    'agency_name': rec.x_studio_field_icWOZ.id,
                    'advisor_name': rec.service_advisor.id,
                    # 'confirmation_date': str(rec.confirmation_date),
                    'vehicle_name': rec.car_name.name,
                    'so_num': self.id,
                    'user_id': rec.user_id.id,
                    'partner_id': rec.partner_id.id,
                })

                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Wheel Checking Report',
                    'res_model': 'wheel_report.wheel_report',
                    'res_id': qc_search_obj.id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'self',
                }
            else:
                print("done2")
                print("Reference")


                check_id = qc_obj.create({
                    'plate_num': rec.vehicle.license_plate,
                    'claim_num': rec.claim_no,
                    'job_card': rec.x_studio_agency_job_card,
                    'agency_name': rec.x_studio_field_icWOZ.id,
                    'advisor_name': rec.service_advisor.id,
                    # 'confirmation_date': str(rec.confirmation_date),
                    'vehicle_name': rec.car_name.name,
                    'so_num': self.id,
                    'user_id': rec.user_id.id,
                    'partner_id': rec.partner_id.id,
                    'line_ids': order_line,

                })
                self.wheel_check_id = check_id.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Wheel Checking Report',
            'res_model': 'wheel_report.wheel_report',
            'res_id': check_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'self',
        }
