# -*- coding: utf-8 -*-
from datetime import datetime,timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil import parser


class ProjectTask(models.Model):
    _inherit = "project.task"

    stage_date = fields.Datetime(string='Stage Date', default=fields.Datetime.now())
    stage_time_ids = fields.One2many('project.task.time', 'project_task_id')
    alloy_digital_signature = fields.Binary(string='Signature', widget="signature")
    is_delivery_stage = fields.Boolean(compute="get_delivery_stage")
    stage_date_2 =fields.Datetime(string='Stage Date')
    is_delete_stage =fields.Boolean(string='Delete Task ',default=False)

    @api.depends('stage_id')
    def get_delivery_stage(self):
       d1=datetime.now()
        for record in self:
            if record.stage_id.name == 'Delivery':
                record.is_delivery_stage = True
                if self.stage_date_2 :
                    if ( self.stage_date_2  < d1  ):
                        record.is_delete_stage =True


    @api.multi
    def write(self, values):
        if 'stage_id' in values:
            new_stage = self.env['project.task.type'].browse(values['stage_id'])
            old_stage = self.stage_id.name
            stage_time_id = self.env['project.task.time']
            if new_stage.name == 'Delivery' and old_stage != 'Finished and QC':
                raise UserError(_("You must go to Finished and QC stage first"))
            stage_time_id.create({
                'project_task_id': self.id,
                'stage_from_id': self.stage_id.id,
                'stage_to_id': new_stage.id,
                'date_from': self.stage_date,
                'date_to': fields.Datetime.now(),
            })

            self.stage_date = fields.Datetime.now()
            self.stage_date_2 =   self.stage_date+timedelta(days=2)

            if self.env.user.stage_ids and values['stage_id'] in self.env.user.stage_ids.ids:
            
                if self.stage_id.id != 73 or self.task_run == True:
                    return super(ProjectTask, self).write(values)
                else :
                    raise UserError(_("You aren't allowed to change to this stage press run Task"))
            else:
                raise UserError(_("You aren't allowed to change to this stage"))
        elif 'alloy_digital_signature' in values:
            old_stage = self.env['project.task.type'].search([('name', '=', 'Delivery')], limit=1)
            new_stage = self.env['project.task.type'].search([('name', '=', 'signature')], limit=1)
            stage_time_id = self.env['project.task.time']
            if new_stage and old_stage:
                stage_time_id.create({
                    'project_task_id': self.id,
                    'stage_from_id': old_stage.id,
                    'stage_to_id': new_stage.id,
                    'date_from': self.stage_date,
                    'date_to': fields.Datetime.now(),
                })
            self.stage_date = fields.Datetime.now()
            return super(ProjectTask, self).write(values)
        else:
            return super(ProjectTask, self).write(values)


class ProjectTaskTime(models.Model):
    _name = "project.task.time"

    project_task_id = fields.Many2one('project.task')
    stage_from_id = fields.Many2one('project.task.type')
    stage_to_id = fields.Many2one('project.task.type')
    date_from = fields.Datetime('Date From')
    date_to = fields.Datetime('Date To')
    time_between_stages = fields.Float(compute="calculate_timer")
    total_time = fields.Char(compute="calculate_timer")

    @api.onchange('date_from', 'date_to')
    @api.depends('date_from', 'date_to')
    def calculate_timer(self):
        for record in self:
            if record.date_from and record.date_to:
                t1 = datetime.strptime(str(record.date_from), '%Y-%m-%d %H:%M:%S')
                t2 = datetime.strptime(str(record.date_to), '%Y-%m-%d %H:%M:%S')
                t3 = t2 - t1
                record.total_time = t3
                record.time_between_stages = float(t3.days) * 24 + (float(t3.seconds) / 3600)