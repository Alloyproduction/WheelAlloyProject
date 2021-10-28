from odoo import fields, api, models, _
from datetime import date
from odoo.exceptions import UserError, ValidationError


class Saudi(models.Model):
    _name = 'gosi.payslip'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GOSI Record'

    employee = fields.Many2one('hr.employee', string="Employee", required=True)
    department = fields.Char(string="Department", required=True)
    position = fields.Char(string='Job Position', required=True)
    nationality = fields.Char(string='Nationality', required=True)
    type_gosi = fields.Char(string='Type', required=True, track_visibility='onchange')
    dob = fields.Char(string='Date Of Birth', required=True)
    gos_numb = fields.Char(string='GOSI Number', required=True, track_visibility='onchange')
    issued_dat = fields.Char(string='Issued Date', required=True, track_visibility='onchange')
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    # _sql_constraints = [('employee_uniq', 'unique (employee, gos_numb)',
    #                      'You can`t have 2 records for the same employee')]

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('gosi.payslip')
        return super(Saudi, self).create(vals)

    @api.onchange('employee')
    def onchange_employee(self):
        for rec in self:
            if rec.employee:
                department = rec.employee
                rec.department = department.department_id.name if department.department_id else False
                rec.position = department.job_id.name
                rec.nationality = department.country_id.name
                rec.type_gosi = department.type
                rec.dob = department.birthday
                rec.gos_numb = department.gosi_number
                rec.issued_dat = department.issue_date

    # @api.constrains('employee')
    @api.onchange('employee', 'gos_numb')
    def _check_employee(self):
        for rec in self:
            # print("emp.")
            if rec.employee:
                # print("emuuu")
                domain = ['|', ('employee', '=', rec.employee.id), ('gos_numb', '=', rec.gos_numb), ]
                recemployee = self.search_count(domain)
                if recemployee:
                    raise ValidationError(_('You can not have 2 records for the same employee'))


class Gosi(models.Model):
    _inherit = 'hr.employee'

    type = fields.Selection([('saudi', 'Saudi')], string='Type')
    gosi_number = fields.Char(string='GOSI Number')
    issue_date = fields.Date(string='Issued Date')
    age = fields.Char(string='AGE', required=False, readonly=True)

    @api.onchange('birthday')
    def onchange_get_age(self):
        for emp in self:
            if emp.birthday:
                todays_date = date.today()
                print("Current year:", todays_date.year)
                time_difference = todays_date.year - emp.birthday.year
                emp.age = time_difference
                print("emp.age:", emp.age)
            else:
                emp.age = 0

    limit = fields.Boolean(string='Eligible For GOSI', default=False, readonly=True)

    @api.onchange('age', 'country_id')
    def compute_age(self):
        for res in self:
            # print('country==', res.country_id.name)
            # print('country==', res.country_id.code)
            # if int(res.age) <= 60 and int(res.age) >= 18:
            if 60 >= int(res.age) >= 18 and res.country_id.code == 'SA':
                res.limit = True
            else:
                res.limit = False


class Pay(models.Model):
    _inherit = 'hr.payslip'

    gosi_no = fields.Many2one('gosi.payslip', string='GOSI Reference', readonly=True)

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            gosi_no = rec.env['gosi.payslip'].search([('employee', '=', rec.employee_id.name)])
            rec.gosi_no = gosi_no.id
