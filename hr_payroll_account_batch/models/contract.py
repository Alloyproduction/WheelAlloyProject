
from odoo import api, models, fields, _
from datetime import date, timedelta
import datetime



class AccountMoveLine(models.Model):
    _inherit = 'hr.contract'

    city_id = fields.Many2one("res.city", string="City",)


    analytic_tags_id  = fields.Many2many('account.analytic.tag','contract_analytical_tags_rel',string= 'Analytic Tags')

    class AccountMoveLine(models.Model):
        _inherit = 'account.move.line'

        city_id = fields.Many2one("res.city", string="City", )

        department_id = fields.Many2one('hr.department', 'Department')

