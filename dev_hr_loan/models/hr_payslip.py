# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def _installment_ids_domain(self):
        print('_installment_ids_domain')
        all_installment_id = self.env['installment.line'].search([('employee_id', '=', self.employee_id.id), ('is_paid', '=', False)])
        # print('all_installment_id', all_installment_id.ids)
        # print('self.employee_id.id', self.employee_id.id)
        domain = [('id', 'in', all_installment_id.ids)]
        # print('domain', domain)
        return domain

    @api.onchange('employee_id', 'number', 'line_ids')
    # @api.multi
    def _installment_ids_onchange(self):
        print('installment_ids_onchange')
        return {'domain': {'installment_ids': [('employee_id', '=', self.employee_id.ids),
                                               ('is_paid','=',False)]}}

    installment_ids = fields.Many2many('installment.line', string='Installment Lines', domain=_installment_ids_domain)
    installment_amount = fields.Float('Installment Amount',compute='get_installment_amount')
    installment_int = fields.Float('Installment Amount',compute='get_installment_amount')

    def compute_sheet(self):
        installment_ids = self.env['installment.line'].search(
                [('employee_id', '=', self.employee_id.id), ('loan_id.state', '=', 'done'),
                 ('is_paid', '=', False),('date','<=',self.date_to)])
        if installment_ids:
            self.installment_ids = [(6, 0, installment_ids.ids)]
            # print('installment_ids2==', self.installment_ids)
        return super(hr_payslip,self).compute_sheet()


    @api.depends('installment_ids')
    def get_installment_amount(self):
        for payslip in self:
            amount = 0
            int_amount = 0
            if payslip.installment_ids:
                for installment in payslip.installment_ids:
                    if not installment.is_skip:
                        amount += installment.installment_amt
                    int_amount += installment.ins_interest

            payslip.installment_amount = amount
            payslip.installment_int = int_amount

    @api.onchange('employee_id')
    def onchange_employee(self):
        if self.employee_id:
            installment_ids = self.env['installment.line'].search(
                [('employee_id', '=', self.employee_id.id), ('loan_id.state', '=', 'done'),
                 ('is_paid', '=', False),('date','<=',self.date_to)])
            if installment_ids:
                self.installment_ids = [(6, 0, installment_ids.ids)]

    @api.onchange('installment_ids')
    def onchange_installment_ids(self):
        if self.employee_id:
            installment_ids = self.env['installment.line'].search(
                [('employee_id', '=', self.employee_id.id), ('loan_id.state', '=', 'done'),
                 ('is_paid', '=', False), ('date', '<=', self.date_to)])
            if installment_ids:
                self.installment_ids = [(6, 0, installment_ids.ids)]

    def action_payslip_done(self):
        res = super(hr_payslip, self).action_payslip_done()
        if self.installment_ids:
            for installment in self.installment_ids:
                # if not installment.is_skip:
                installment.is_paid = True
            installment.payslip_id = self.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
