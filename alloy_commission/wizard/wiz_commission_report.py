# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CommissionReportWizard(models.TransientModel):
    _name = "commission.report.wizard"
    date_from = fields.Date(string='Date From', default=fields.date.today())
    date_to = fields.Date(string='Date To', default=fields.date.today())
    filter_by = fields.Selection(selection=[('advisor', 'Advisor'),
                                            ('customer', 'Customer'),
                                            ('both', 'Both'),
                                            ], default='advisor')
    advisor_id = fields.Many2one('res.partner', string='service advisor')
    customer_id = fields.Many2one('res.partner', string='Customer')

    def check_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'filter_by': self.filter_by,
                'advisor_id': self.advisor_id[0] if self.advisor_id else False,
                'customer_id': self.customer_id[0] if self.customer_id else False,
            },
        }
        return self.env.ref('alloy_commission.action_report_account_commission').report_action(self, data=data)
