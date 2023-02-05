# -*- coding: utf-8 -*-
from datetime import datetime,timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil import parser


class ProjectTask(models.Model):
    _inherit = "project.task"

    stage_date = fields.Datetime(string='Stage Date', default=lambda self: fields.Datetime.now())
    stage_time_ids = fields.One2many('project.task.time', 'project_task_id')
    alloy_digital_signature = fields.Binary(string='Signature', widget="signature")
    is_delivery_stage = fields.Boolean()
    stage_date_2 = fields.Datetime(string='Stage Date')
    is_delete_stage = fields.Boolean(string='Delete Task',default=False)

    line_ids = fields.One2many('product.task.used', 'request_id',
                               'Product Used',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')




    @api.multi
    def write(self, values):
        if 'stage_id' in values:
            new_stage = self.env['project.task.type'].browse(values['stage_id'])
            old_stage = self.stage_id.name
            stage_time_id = self.env['project.task.time']
            if new_stage.name == 'Delivery' and old_stage != 'Finished and QC' :
                if  old_stage != 'Waiting':
                    raise UserError(_("You must go to Finished and QC stage first"))
            stage_time_id.create({
                'project_task_id': self.id,
                'stage_from_id': self.stage_id.id,
                'stage_to_id': new_stage.id,
                'date_from': self.stage_date,
                'date_to': fields.Datetime.now(),
            })
            d1 = datetime.now()
            stage_tasks = self.env['project.task'].search(
                [('stage_date_2', '<', d1), ('is_delete_stage', '=', False), ('stage_id.name','=','Delivery')])
            self.stage_date = fields.Datetime.now()
            if new_stage.name == 'Delivery':
                self.stage_date_2 = self.stage_date + timedelta(days=2)
                print(self.stage_date_2)
                for line in stage_tasks:
                    print(line)
                    print(line.stage_date_2)
                    line.is_delete_stage = True
                    print(line.is_delete_stage)

                # x = self.env['project.task'].search([])
                # for i in x:
                #     if new_stage.name == 'Delivery':
                #         if i.stage_date_2:
                #             if i.stage_date_2 < d1:
                #                i.is_delete_stage = True

            if self.env.user.stage_ids and values['stage_id'] in self.env.user.stage_ids.ids:

                if self.stage_id.id != 73 or self.task_run == True:
                    return super(ProjectTask, self).write(values)
                else :
                    return super(ProjectTask, self).write(values)
                # if self.stage_id.id != 73 or self.task_run == True:
                #     return super(ProjectTask, self).write(values)
                # else :
                #     raise UserError(_("You aren't allowed to change to this stage press run Task"))
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

##########################################################################################################################################

class TaskProduct(models.Model):
    _name = "product.task.used"


    @api.depends('product_id')
    def _get_unit_cost(self):
        for rec in self:
            rec.product_cost = rec.product_id.unit_cost



    @api.depends('product_id')
    def _get_unit(self):
        for rec in self:
            rec.used_unit = rec.product_id.used_product_unit

    @api.depends('product_id')
    def _get_main_unit(self):
        for rec in self:
            rec.product_uom_id = rec.product_id.uom_id.name

    @api.depends('task_number')
    def _get_project(self):
        for rec in self:
            rec.project_name = rec.task_number.project_id

    @api.depends('task_number')
    def _get_sale_id(self):
        for rec in self:
            if rec.task_number.sale:
               rec.sale_name = rec.task_number.sale_id




    user_id = fields.Many2one('res.users', string='User', ondelete='cascade', track_visibility='onchange', default=lambda self: self.env.user, readonly=True,)
    create_date = fields.Datetime(string= 'Date', default=fields.Datetime.now)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],required=True)
    product_uom_id = fields.Many2one(compute="_get_main_unit", readonly=True, string='Product Unit of Measure')
    product_qty = fields.Float(string='Quantity')
    product_cost = fields.Float( string="Product Cost", compute="_get_unit_cost", readonly=True, digits=(12, 3))
    used_unit = fields.Char(string='Used Unit of Measure', compute="_get_unit", readonly=True)
    total_cost = fields.Float(string="Total Cost", readonly=True,compute="_get_total_cost", digits=(12, 3))
    request_id = fields.Many2one('project.task','Product Used', ondelete='cascade', readonly=True)
    task_number = fields.Many2one('project.task', string="Task Name")
    project_name = fields.Many2one('project.project', string="Project Name", track_visibility='onchange' , compute="_get_project", readonly=True)
    sale_name = fields.Many2one('sale.order', 'Sales Order', compute="_get_sale_id", readonly=True)

    @api.depends('product_cost', 'product_qty', 'total_cost')
    def _get_total_cost(self):
        print("yes")
        for r in self:
            r.total_cost = r.product_cost * r.product_qty
            print("done")



    # product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'))
    # price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
    # qty_ordered = fields.Float(compute='_compute_ordered_qty', string='Ordered Quantities')

    class ProductUsedTemplate(models.Model):
        _inherit = 'product.template'

        used_product_unit = fields.Selection([('m_mel', 'ML'),
                                              ('m_gram', 'Gram'),
                                              ('m_cm', 'CM'),
                                              ('m_pic', 'Pic'),
                                              ('m_roll', 'Roll'),
                                              ('m_unite', 'Unite'), ])
        unit_cost = fields.Float(string="Unit Cost")

        # @api.onchange('used_product_unit')
        @api.onchange('uom_id')
        def _get_total_cost(self):
         if self.uom_id.name:
            for i in self:
                str = i.uom_id.name
                lis = str.split()
                unit1 = lis[0]
                musure = lis[1]

                if musure == "LTR" or musure == "LTR(S)" or musure == "Litre(s)":
                    total = (self.standard_price / float(unit1))
                    total=total/1000
                    i.unit_cost= total
                    i.used_product_unit = "m_mel"

                if musure == "ML":
                    total = (self.standard_price / float(unit1))
                    i.unit_cost= total
                    i.used_product_unit = "m_mel"


                if musure == "KG" or musure == "kg(s)" or musure == "KG(S)":
                    total = (self.standard_price / float(unit1))
                    total = total / 1000
                    i.unit_cost = total
                    i.used_product_unit = "m_gram"

                if musure == "GRAMS":
                    total = (self.standard_price / float(unit1))
                    i.unit_cost = total
                    i.used_product_unit = "m_gram"

                if musure == "Meter":
                    total = (self.standard_price / float(unit1))
                    total = total / 1000
                    i.unit_cost = total
                    i.used_product_unit = "m_cm"

                if musure == "CM":
                    total = (self.standard_price / float(unit1))
                    i.unit_cost = total
                    i.used_product_unit = "m_cm"

                if musure == "PCS" or musure == "Pc(s)":
                    total = (self.standard_price / float(unit1))
                    i.unit_cost= total
                    i.used_product_unit = "m_pic"

                if musure == "Roll":
                    total = (self.standard_price / float(unit1))
                    total = total / 6
                    i.unit_cost = total
                    i.used_product_unit = "m_roll"


                if musure == "Day" or musure == "EA" or musure == "GAL" or musure == "KIT" or musure == "LBS" or musure == "TON" or musure == "BOX" or musure == "Bottle" or musure == "Month" or musure == "Year" or musure == "Lines" :
                    total = (self.standard_price / float(unit1))
                    i.unit_cost = total
                    i.used_product_unit = "m_unite"

