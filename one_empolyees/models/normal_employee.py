# -*- coding: utf-8 -*-

# from odoo import models, fields, api
from urllib import request

from odoo import api, fields, models, _


class EmpForm(models.Model):
    _name = 'emp.form'
    _description = 'Normal Employee View'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', required=True)
    emp_image = fields.Binary(compute="_emp_image1", store=True)

    emp_job_id = fields.Many2one('hr.job', compute="_compute_employee", readonly=True, string="Job Position")
    emp_manager_id = fields.Many2one('hr.employee', compute="_compute_employee", readonly=True, string="Manager")

    emp_dt_id = fields.Many2one('hr.department', compute="_compute_employee", readonly=True, string="Department")
    emp_dt_manager_id = fields.Many2one('hr.employee', compute="_compute_employee", readonly=True,
                                        string="Department Manager")

    identification_no = fields.Char(compute="_compute_employee", readonly=True, string="Identification Number")
    residency_no = fields.Char(compute="_compute_employee", readonly=True, string="Visa No")
    job_no = fields.Char(compute="_compute_employee", readonly=True, string="Job title")

    @api.depends('employee_id')
    def _compute_employee(self):
        for i in self.filtered('employee_id'):
            i.emp_job_id = i.employee_id.job_id
            i.emp_manager_id = i.employee_id.parent_id
            i.emp_dt_id = i.employee_id.department_id
            i.emp_dt_manager_id = i.employee_id.department_id.manager_id
            i.identification_no = i.employee_id.identification_id
            i.residency_no = i.employee_id.visa_no
            i.job_no = i.employee_id.job_title

    @api.depends('employee_id.image')
    def _emp_image1(self):
        self.emp_image = self.employee_id.image

    # loan
    def document_view_ticket(self):
        self.ensure_one()
        domain = [
            ('employee_id', '=', self.employee_id.id)]

        return {
            'name': _('Loans'),
            'domain': domain,
            'res_model': 'employee.loan',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click To Create For New Records
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_id': %s}" % self.employee_id.id
        }

    # Skip Installment
    def create_skip_installment(self):
        self.ensure_one()
        domain = [
            ('employee_id', '=', self.employee_id.id)]
        return {
            'name': _('Skip Installment'),
            'domain': domain,
            'res_model': 'dev.skip.installment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click To Create Skip Installment
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_id': %s}" % self.employee_id.id
        }

    def _document_count_ticket(self):
        for each in self:
            document_ids2 = self.env['employee.loan'].sudo().search([('employee_id', '=', each.employee_id.id)])
            each.document_count_ticket = len(document_ids2)

    document_count_ticket = fields.Integer(compute='_document_count_ticket', string='# Loans')


    def count_skip(self):
        for each in self:
            skip_id = self.env['dev.skip.installment'].sudo().search([('employee_id', '=', each.employee_id.id)])
            each.count_skip_inst = len(skip_id)

    count_skip_inst = fields.Integer(compute='count_skip', string='# skip')
