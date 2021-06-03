from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)
grey = "\x1b[38;21m"
yellow = "\x1b[33;21m"
red = "\x1b[31;21m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"
green = "\x1b[32m"
blue = "\x1b[34m"


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _get_join_date(self):
        contract_id = self.env['hr.contract'].search([('employee_id', '=', self.id),
                                                      ('state', '=', 'open')
                                                      ], order='id asc', limit=1)
        if contract_id:
            self.join_date = contract_id.date_start

    join_date = fields.Date(default=_get_join_date)
    working_date = fields.Date("Rejoin Date")


