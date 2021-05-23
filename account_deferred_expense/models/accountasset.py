# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta, parser




class AccountAssetCategory(models.Model):

    _inherit = 'account.asset.category'


    type = fields.Selection([('sale', 'Sale: Revenue Recognition'), ('purchase', 'Purchase: Asset'),('expense', 'Deferred Expense')], required=True,
                        index=True, default='purchase')


class AccountAsset(models.Model):

    _inherit = 'account.asset.asset'

    @api.multi
    def compute_depreciation_board(self):
        super(AccountAsset, self).compute_depreciation_board()
        i=0
        last_index= len(self.depreciation_line_ids)
        print(self.depreciation_line_ids)
        print(last_index)
        if self.depreciation_line_ids:
            d1 = self.depreciation_line_ids[0].depreciation_date
            d2 =self.depreciation_line_ids[-1].depreciation_date
            noofdays= d1-d2
            print("noofdays",abs(noofdays.days))
            nodays=abs(noofdays.days)
            costperDay =  self.value/nodays
            i=0
            Cost_no_days=0
            depreciation_value =0
            for rec in self.depreciation_line_ids:
                print(i,rec.depreciation_date)
                # mydate= self.date
                print(" rec.depreciation_date ", rec.depreciation_date)
                current_day=rec.depreciation_date.day
                last_day = parser.parse(str(rec.depreciation_date)) + relativedelta.relativedelta(months=+1, day=1, days=-1)
                last_day= last_day.day

                if i==0 :

                    Cost_no_days = (last_day - current_day +1) * costperDay
                    depreciation_value= Cost_no_days
                    rec.depreciated_value = Cost_no_days

                    rec.amount = Cost_no_days
                    rec.remaining_value = self.value - rec.depreciated_value

                elif i== last_index-1 :
                    Cost_no_days =  (current_day-1 ) * costperDay

                    depreciation_value += Cost_no_days
                    rec.depreciated_value = depreciation_value
                    rec.remaining_value = self.value - depreciation_value

                    rec.amount = Cost_no_days

                else :
                    print(i, rec.depreciation_date)
                    rec.depreciation_date = rec.depreciation_date.replace(day=last_day)
                    Cost_no_days = last_day * costperDay

                    depreciation_value +=  Cost_no_days
                    rec.depreciated_value = depreciation_value
                    rec.remaining_value = self.value - depreciation_value

                    rec.amount = Cost_no_days




                i+=1
