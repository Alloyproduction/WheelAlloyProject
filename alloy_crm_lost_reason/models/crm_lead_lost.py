# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLeadLostinherit(models.TransientModel):
    _inherit = 'crm.lead.lost'
    _description = 'Get Lost Reason'

    explain_lost_reason_id = fields.Char(string="Explain#")

    @api.multi
    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        leads.write({'is_lost': True})
        leads.write({'lost_reason': self.lost_reason_id.id})
        leads.write({'explain_lost_reason': self.explain_lost_reason_id})
        leads.write({'active': True})
        leads.write({'stage_id': 6})

        return leads.action_set_lost()


        # @api.multi
        # def action_lost_reason_apply(self):
        #     leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        #     leads.write({'lost_reason': self.lost_reason_id.id})
        #     return leads.action_set_lost()

