# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'


    hra = fields.Monetary(string='HRA', tracking=True, help="House rent allowance.")
    travel_allowance = fields.Monetary(string="Travel Allowance", help="Travel allowance")
    conv_allowance = fields.Monetary(string="Conveyance Allowance", help="Conveyance Allowance")

    insurances = fields.Monetary(string="Insurances", help="Insurances")

    loan_allowance = fields.Monetary(string="Loan", help="Loan")
    advance_allowance = fields.Monetary(string="Advance", help="Advance")
    gosi_allowance = fields.Monetary(string="Gosi", help="Gosi")
    other_deduction = fields.Monetary(string="Other Deduction", help="Other Deduction")
    other_allowance = fields.Monetary(string="Other Allowance", help="Other allowances")
