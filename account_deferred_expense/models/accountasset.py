# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta, parser


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    type = fields.Selection(
        [('sale', 'Sale: Revenue Recognition'), ('purchase', 'Purchase: Asset'), ('expense', 'Deferred Expense')],
        required=True,
        index=True, default='purchase')


class AccountAsset(models.Model):
    _inherit = 'account.asset.asset'
    Hijri_no_days = fields.Integer(string='No of days ')

    @api.multi
    def compute_depreciation_board(self):

        super(AccountAsset, self).compute_depreciation_board()
        i = 0
        last_index = len(self.depreciation_line_ids)
        # print(self.depreciation_line_ids)
        # print(last_index)
        if self.depreciation_line_ids:
            d1 = self.depreciation_line_ids[0].depreciation_date
            d2 = self.depreciation_line_ids[-1].depreciation_date
            noofdays = d1 - d2
            # print(self.Hijri_no_days)
            if self.Hijri_no_days > 0:
                nodays = self.Hijri_no_days

            else:
                nodays = abs(noofdays.days)

            # print("noofdays", abs(nodays))
            costperDay = self.value / nodays
            # print(costperDay)
            i = 0
            Cost_no_days = 0
            depreciation_value = 0
            total_value = 0
            total__days = 0
            total_d_in_this_month = 0
            for rec in self.depreciation_line_ids:
                # print(i, rec.depreciation_date)
                # mydate= self.date
                # print(" rec.depreciation_date ", rec.depreciation_date)
                current_day = rec.depreciation_date.day
                last_day = parser.parse(str(rec.depreciation_date)) + relativedelta.relativedelta(months=+1, day=1,
                                                                                                  days=-1)
                last_day_of_month = parser.parse(str(rec.depreciation_date)) + relativedelta.relativedelta(months=+1, day=1,
                                                                                                  days=-1)
                # print('last day in m', last_day)
                # print('last day in mmm', last_day_of_month.strftime('%Y-%m-%d'))
                last_day = last_day.day
                # print('last daaaay in m', last_day)
                if i == 0:
                    # M
                    rec.depreciation_date = last_day_of_month.strftime('%Y-%m-%d')
                    # print(" rec.depreciation_date for first line ", rec.depreciation_date)
                    total_d_in_this_month += (last_day - current_day + 1)
                    # print('num of d in this month', total_d_in_this_month)
                    total__days += (last_day - current_day + 1)
                    # print('total__daysss', total__days)
                    Cost_no_days = (last_day - current_day + 1) * costperDay
                    depreciation_value = Cost_no_days
                    rec.depreciated_value = Cost_no_days
                    rec.amount = Cost_no_days
                    rec.remaining_value = self.value - rec.depreciated_value
                    if self.Hijri_no_days > 0:
                        total_value += rec.amount
                        # total_d_in_this_month += (last_day - current_day + 1)
                        # print('num of d in this month HH=', total_d_in_this_month)
                elif i == last_index - 1:
                    if self.Hijri_no_days > 0:
                        # print("total_value" ,total_value)
                        # Remain_last_month=(self.value - total_value)
                        # rec.amount =  Remain_last_month
                        # rec.remaining_value = 0

                        # M
                        # last_month_days = (self.Hijri_no_days - total__days) + 18
                        last_month_days = (self.Hijri_no_days - total__days)
                        print("num=",last_month_days)
                        rec.depreciation_date = rec.depreciation_date.replace(day=last_month_days)
                        print('last_date', rec.depreciation_date)
                        # print("total days", total__days)
                        Cost_no_days = (self.Hijri_no_days - total__days) * costperDay
                        depreciation_value += Cost_no_days
                        rec.depreciated_value = depreciation_value
                        rec.remaining_value = self.value - depreciation_value
                        rec.amount = Cost_no_days
                    else:
                        Cost_no_days = (current_day - 1) * costperDay
                        depreciation_value += Cost_no_days
                        rec.depreciated_value = depreciation_value
                        rec.remaining_value = self.value - depreciation_value
                        rec.amount = Cost_no_days
                        # total_value += rec.amount
                else:
                    # print(i, rec.depreciation_date)
                    rec.depreciation_date = rec.depreciation_date.replace(day=last_day)
                    total__days += last_day
                    # print("total days for all in M=", total__days)
                    Cost_no_days = last_day * costperDay
                    depreciation_value += Cost_no_days
                    rec.depreciated_value = depreciation_value
                    rec.remaining_value = self.value - depreciation_value
                    rec.amount = Cost_no_days
                    if self.Hijri_no_days > 0:
                        total_value += rec.amount
                i += 1
