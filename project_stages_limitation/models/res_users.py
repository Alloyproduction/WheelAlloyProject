# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = "res.users"

    stage_ids = fields.Many2many(comodel_name="project.task.type")
