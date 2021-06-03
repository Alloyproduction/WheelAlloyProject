from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    no_of_days_per_year = fields.Float('No Of Days Per Year', default=365)
    # allocation_type = fields.Selection([('Daily', 'Daily'),
    #                                     ('Monthly', 'Monthly'),
    #                                     ('Yearly', 'Yearly'), ], default='Daily')
    leave_type_id = fields.Many2one('hr.leave.type',
                                    domain=[('allocation_type', '=', 'fixed')])
    leave_id = fields.Many2one('hr.leave.type')
    unpaid_type = fields.Selection([('Add', 'Add'),
                                    ('Ignore', 'Ignore')], default='Add'
                                   )
    first_period = fields.Float(default=5)
    deserve_first_period = fields.Float(default=21)
    second_period = fields.Float()
    deserve_second_period = fields.Float(default=30)


class AllocationConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    no_of_days_per_year = fields.Float('No Of Days Per Year',
                                       default=lambda self: self.env.user.company_id.no_of_days_per_year)
    # allocation_type = fields.Selection([('Daily', 'Daily'),
    #                                     ('Monthly', 'Monthly'),
    #                                     ('Yearly', 'Yearly'), ],
    #                                    default=lambda self: self.env.user.company_id.allocation_type)
    leave_type_id = fields.Many2one('hr.leave.type', string='Annual Leave',
                                    default=lambda self: self.env.user.company_id.leave_type_id,
                                    domain=[('allocation_type', '=', 'fixed')])
    unpaid_type = fields.Selection([('Add', 'Add'),
                                    ('Ignore', 'Ignore')],
                                   default=lambda self: self.env.user.company_id.unpaid_type
                                   )
    leave_id = fields.Many2one('hr.leave.type', string='Unpaid Leave',
                               default=lambda self: self.env.user.company_id.leave_id)
    first_period = fields.Float(default=lambda self: self.env.user.company_id.first_period)
    deserve_first_period = fields.Float(default=lambda self: self.env.user.company_id.deserve_first_period)
    second_period = fields.Float(default=lambda self: self.env.user.company_id.second_period)
    deserve_second_period = fields.Float(default=lambda self: self.env.user.company_id.deserve_second_period)

    @api.model
    def create(self, vals):
        if 'company_id' in vals or 'no_of_days_per_year' in vals \
                or 'leave_type_id' in vals \
                or 'unpaid_type' in vals or 'first_period' in vals \
                or 'deserve_first_period' in vals or 'second_period' in vals \
                or 'deserve_second_period' in vals \
                or 'leave_id' in vals:
            self.env.user.company_id.write({
                'no_of_days_per_year': vals['no_of_days_per_year'],
                'leave_type_id': vals['leave_type_id'],
                'unpaid_type': vals['unpaid_type'],
                'first_period': vals['first_period'],
                'deserve_first_period': vals['deserve_first_period'],
                'second_period': vals['second_period'],
                'deserve_second_period': vals['deserve_second_period'],
                'leave_id': vals['leave_id'],
            })
        res = super(AllocationConfigSettings, self).create(vals)
        res.company_id.write({
            'no_of_days_per_year': vals['no_of_days_per_year'],
            'leave_type_id': vals['leave_type_id'],
            'unpaid_type': vals['unpaid_type'],
            'first_period': vals['first_period'],
            'deserve_first_period': vals['deserve_first_period'],
            'second_period': vals['second_period'],
            'deserve_second_period': vals['deserve_second_period'],
            'leave_id': vals['leave_id'],
        })
        return res
