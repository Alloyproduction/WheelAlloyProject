# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT



class my_equipment_request(models.Model):
    _name = "overtime.request"
    _rec_name = "employee_id"
    _description = "Overtime Request"
    _order = 'year desc, employee_id desc'
    # @api.multi
    # @api.depends('end_date', 'start_date')
    # def _compute_num_of_hours(self):
    #     for line in self:
    #         if line.start_date and line.end_date:
    #             diff = line.end_date - line.start_date
    #             days, seconds = diff.days, diff.seconds
    #             hours = days * 24 + seconds // 3600
    #             line.num_of_hours = hours
    #     return

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True)
    # employee_id = fields.Char(string="Employee", required=True, readonly=True)
    # start_date = fields.Datetime(string="Start Date", required=True, default=fields.datetime.now(), readonly=True)
    start_date = fields.Date(string="Start Date", required=True, readonly=True)
    end_date = fields.Date(string="End Date", required=True, readonly=True)
    department_id = fields.Many2one('hr.department', string="Department")
    department_manager_id = fields.Many2one('hr.employee', string="Manager")
    include_in_payroll = fields.Boolean(string="Include In Payroll", default=True)
    month = fields.Integer('month', store=True)
    year = fields.Char('Year', store=True)
    month_n = fields.Char('Month', store=True)

    approve_date = fields.Datetime(string="Approve Date", readonly=True)
    approve_by_id = fields.Many2one('res.users', string="Approve By", readonly=True)

    dept_approve_date = fields.Datetime(string="Department Approve Date", readonly=True)
    dept_manager_id = fields.Many2one('res.users', string="Department Manager", readonly=True)

    # num_of_hours = fields.Float(string="Number Of Hours", compute="_compute_num_of_hours")
    num_of_hours = fields.Float(string="Total Overtime in minutes")
    total_delay_hours = fields.Float(string="Total Delay in minutes")
    num_of_hours2 = fields.Float(string="Number Of minutes")

    notes = fields.Text(string="Notes")

    state = fields.Selection([('new', 'New'), ('first_approve', 'Waiting For First Approve'),
                              ('dept_approve', 'Waiting For Department Approve'),
                              ('done', 'Done'), ('refuse', 'Refuse')], string="State", default='new')

    @api.constrains('end_date', 'start_date')
    def check_end_date(self):
        if self.end_date < self.start_date:
            raise Warning(_('End Date must be after the Start Date!!'))

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.department_id = self.employee_id.department_id.id
        self.department_manager_id = self.employee_id.department_id.manager_id.id

    def confirm_action(self):
        self.write({'state': 'first_approve'})
        return

    def back_to_new(self):
        self.write({'state': 'new'})
        return

    def first_approve_action(self):
        self.write({'state': 'dept_approve',
                    'approve_by_id': self.env.user.id,
                    'approve_date': fields.datetime.now()})
        return

    def dept_approve_action(self):
        self.write({'state': 'done',
                    'dept_manager_id': self.env.user.id,
                    'dept_approve_date': fields.datetime.now()})
        return
        # return {
        #     'name': _('Overtime'),
        #     'res_model': 'bt.hr.overtime',
        #     'type': 'ir.actions.act_window',
        #     'view_id': False,
        #     'view_mode': 'tree,form',
        #     'view_type': 'form',
        #     'help': _('''<p class="oe_view_nocontent_create">
        #                                        Click To Create For New Records
        #                                     </p>'''),
        #     'limit': 80,
        #     'context': "{'default_employee_id': %s}" % self.employee_id.id
        # }

    def refuse_action(self):
        self.write({'state': 'refuse'})
        return
