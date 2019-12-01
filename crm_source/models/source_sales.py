# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CrmLeadSource(models.Model):
    _name = "crm.lead.source"
    name = fields.Char()


class CrmLead(models.Model):
    _inherit = "crm.lead"

    crm_source_id2 = fields.Many2one("utm.source", 'Source')
    # crm_source_id = fields.Many2one("crm.lead.source", 'Source')
