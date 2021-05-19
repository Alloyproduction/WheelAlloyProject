# -*- coding: utf-8 -*-

from odoo import api, models, fields
import re


class ReportPeriodicalSale(models.AbstractModel):
    _name = 'report.alloy_commission.report_account_commission'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from'] if data['form']['date_from'] else fields.date.today()
        date_to = data['form']['date_to'] if data['form']['date_to'] else fields.date.today()
        filter_by = data['form']['filter_by']
        advisor_id = data['form']['advisor_id']
        customer_id = data['form']['customer_id']
        total_cost = 0.0
        total_qty = 0.0
        total_rate = 0.0
        total_commission = 0.0
        advisor = []
        customer = []
        # in ['advisor', 'both']
        if filter_by == 'advisor':
            u = (re.findall(r'\d+', advisor_id))
            for i in u:
                advisor.append(int(i))
            domain = [('date', '>=', date_from),
                      ('date', '<=', date_to),
                      ('advisor_id', '=', advisor[0])]
        elif filter_by == 'customer':
            customer_number = (re.findall(r'\d+', customer_id))
            for c in customer_number:
                customer.append(int(c))
            domain = [('date', '>=', date_from),
                      ('date', '<=', date_to),
                      ('customer_id', '=', customer[0])]
        else:
            u = (re.findall(r'\d+', advisor_id))
            customer_number = (re.findall(r'\d+', customer_id))
            for i in u:
                advisor.append(int(i))
            for c in customer_number:
                customer.append(int(c))
            domain = [('date', '>=', date_from),
                      ('date', '<=', date_to),
                      ('customer_id', '=', customer[0]),
                      ('advisor_id', '=', advisor[0])
                      ]
        account_commissions = []
        commissions = self.env['account.commission'].search(domain)
        for comm in commissions:
            account_commissions.append({
                'name': comm.name,
                'date': comm.date,
                'advisor_id': comm.advisor_id.name,
                'customer_id': comm.customer_id.name,
                'invoice_number': comm.invoice_number,
                'invoice_date': comm.invoice_id.date_invoice,
                'product_id': comm.account_commission_ids[0].product_id.name,
                'description': comm.account_commission_ids[0].description,
                'analytic_account_id': comm.account_commission_ids[0].analytic_account_id.name,
                'analytic_tags_ids': [line.name for line in comm.account_commission_ids[0].analytic_tags_ids],
                'repair_cost': comm.account_commission_ids[0].repair_cost,
                'rims_quantity': comm.account_commission_ids[0].rims_quantity,
                'commission_rate': comm.account_commission_ids[0].commission_rate,
                'commission_amount': comm.account_commission_ids[0].commission_amount,
            })
            total_cost += comm.account_commission_ids[0].repair_cost
            total_qty += comm.account_commission_ids[0].rims_quantity
            total_rate += comm.account_commission_ids[0].commission_rate
            total_commission += comm.account_commission_ids[0].commission_amount
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': date_from,
            'date_to': date_to,
            'account_commissions': account_commissions,
            'total_cost': total_cost,
            'total_qty': total_qty,
            'total_rate': total_rate,
            'total_commission': total_commission,
        }
