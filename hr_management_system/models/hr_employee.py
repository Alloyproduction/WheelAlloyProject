# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.parser import parse
from .calverter import Calverter


class HrSystemEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _get_lang(self):
        return self.env['res.lang'].get_installed()

    emp_lang = fields.Selection(selection='_get_lang', string='Language')
    emp_exp = fields.Char(_('Experience'))
    emp_date_start = fields.Date(_('Work Starting Date'))
    emp_insurance_num = fields.Char(_('Medical insurance number'))
    emp_job_data = fields.Char(_('Job Data'))



    # insurance
    def document_view_insurance(self):
        self.ensure_one()
        domain = [
            ('emp_id', '=', self.id)]

        return {
            'name': _('Medical Insurances'),
            'domain': domain,
            'res_model': 'hr.insurance',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click To Create For New Records
                        </p>'''),
            'limit': 80,
            'context': "{'default_emp_id': %s}" % self.id,
        }

    def _document_count_insurance(self):
        for each in self:
            document_ids2 = self.env['hr.insurance'].sudo().search([('emp_id', '=', each.id)])
            each.document_count_insurance = len(document_ids2)
            # print(document_ids2.emp_id.name)
            # print(self.name)

    document_count_insurance = fields.Integer(compute='_document_count_insurance', string='# Medical Insurance')

    # protection
    def document_view_protection(self):
        self.ensure_one()
        domain = [
            ('emp_id', '=', self.id)]

        return {
            'name': _('Benefits'),
            'domain': domain,
            'res_model': 'hr.protection',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click To Create For New Records
                        </p>'''),
            'limit': 80,
            'context': "{'default_emp_id': %s}" % self.id,
        }

    def _document_count_protection(self):
        for each in self:
            document_ids2 = self.env['hr.protection'].sudo().search([('emp_id', '=', each.id)])
            each.document_count_protection = len(document_ids2)
            # print(document_ids2.emp_id.name)
            # print(self.name)

    document_count_protection = fields.Integer(compute='_document_count_protection', string='# Benefits')


    birthday_hijri = fields.Char(string='Date of Birth Hajri',compute='_calculate_birthday_hajri')

    @api.depends('birthday')
    def _calculate_birthday_hajri(self):
        cal = Calverter()
        if self.birthday:
            d = self.birthday
            jd = cal.gregorian_to_jd(d.year, d.month, d.day)
            hj = cal.jd_to_islamic(jd)
            self.birthday_hijri = str(hj[2]) + "/" + str(hj[1])+ "/" + str(hj[0])
        else:
            self.birthday_hijri = " "
