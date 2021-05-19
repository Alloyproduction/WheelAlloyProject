# -*- coding: utf-8 -*-

from datetime import timedelta, datetime, date

from odoo import api, fields, models, _
from .calverter import Calverter

class ContractDocuments(models.Model):
    _inherit = 'hr.contract'

    hra = fields.Monetary(string='HRA', tracking=True, help="House rent allowance.")
    travel_allowance = fields.Monetary(string="Travel Allowance", help="Travel allowance")
    conv_allowance = fields.Monetary(string="Conveyance Allowance", help="Conveyance Allowance")

    insurances = fields.Monetary(string="Insurances", help="Insurances")

    loan_allowance = fields.Monetary(string="Loan", help="Loan")
    advance_allowance = fields.Monetary(string="Advance", help="Advance")
    gosi_allowance = fields.Monetary(string="Gosi", help="Gosi")
    other_deduction = fields.Monetary(string="Other Deduction", help="Other Deduction")
    other_allowance = fields.Monetary(string="Other Allowance", help="Other allowances")

    date_start_hijri = fields.Char(string='Start Date Hijri', compute='_calculate_start_date_hajri')
    date_end_hijri = fields.Char(string='End Date Hijri', compute='_calculate_date_end_hajri')
    trial_date_end_hijri = fields.Char(string='End Of Trial Hijri', compute='_calculate_trial_date_end_hajri')

    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_contract_rel', 'doc_id', 'attach_contract_id', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)


    @api.depends('date_start')
    def _calculate_start_date_hajri(self):
        cal = Calverter()
        if self.date_start:
            d = self.date_start
            jd = cal.gregorian_to_jd(d.year, d.month, d.day)
            hj = cal.jd_to_islamic(jd)
            self.date_start_hijri = str(hj[2]) + "/" + str(hj[1]) + "/" + str(hj[0])
        else:
            self.date_start_hijri = ""

    @api.depends('date_end')
    def _calculate_date_end_hajri(self):
        cal = Calverter()
        if self.date_end:
            d = self.date_end
            jd = cal.gregorian_to_jd(d.year, d.month, d.day)
            hj = cal.jd_to_islamic(jd)
            self.date_end_hijri = str(hj[2]) + "/" + str(hj[1]) + "/" + str(hj[0])
        else:
            self.date_end_hijri = ""

    @api.depends('trial_date_end')
    def _calculate_trial_date_end_hajri(self):
        cal = Calverter()
        if self.trial_date_end:
            d = self.trial_date_end
            jd = cal.gregorian_to_jd(d.year, d.month, d.day)
            hj = cal.jd_to_islamic(jd)
            self.trial_date_end_hijri = str(hj[2]) + "/" + str(hj[1]) + "/" + str(hj[0])
        else:
            self.trial_date_end_hijri = ""


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_contract_rel = fields.Many2many('hr.contract', 'doc_attachment_id', 'attach_contract_id', 'doc_id',
                                      string="Attachment", invisible=1)
