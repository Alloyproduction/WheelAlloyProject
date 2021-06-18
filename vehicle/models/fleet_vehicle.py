# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression

class Color(models.Model):
    _name = 'color'
    name =fields.Char('Name')


class partner(models.Model):
    _inherit ='res.partner'

    vehicle_ids =fields.One2many('vehicle','owner_id')
    is_insurance = fields.Boolean('Insurance')

class FleetVehicle(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'vehicle'
    _description = 'Vehicle'
    _order = 'model_id asc'

    name = fields.Char(compute="_compute_vehicle_name",store=True)
    is_insured = fields.Boolean('is insured ?')
    insurance_company = fields.Many2one('res.partner',string='Insurance Company')
    active = fields.Boolean('Active', default=True, track_visibility="onchange")
    odometer = fields.Float('Odometer')
    owner_id = fields.Many2one('res.partner',string='Owner',required=False)
    company_id = fields.Many2one('res.company', 'Company')
    license_plate = fields.Char(track_visibility="onchange", required=True,
     help='License plate number of the vehicle (i = plate number for a car)', copy=True)
    vin_sn = fields.Char('Chassis Number', help='Unique number written on the vehicle motor (VIN/SN number)', copy=False)
    driver_id = fields.Many2one('res.partner', 'Driver', track_visibility="onchange", help='Driver of the vehicle', copy=False)
    model_id = fields.Many2one('vehicle.model', 'Car mark',
        track_visibility="onchange", required=True, help='Model of the vehicle')
    brand_id = fields.Many2one('vehicle.model.brand', 'Brand', related="model_id.brand_id", store=True, readonly=False)
    car_name1 = fields.Many2one('vehicle.name', string='Car model',
                                track_visibility="onchange", required=True, help='Name of the vehicle')
    acquisition_date = fields.Date('Immatriculation Date', required=False,
        default=fields.Date.today, help='Date when the vehicle has been immatriculated')
    first_contract_date = fields.Date(string="First Contract Date", default=fields.Date.today)
    color = fields.Many2one('color',help='Color of the vehicle')
    location = fields.Char(help='Location of the vehicle (garage, ...)')
    seats = fields.Integer('Seats Number', help='Number of seats of the vehicle')
    model_year = fields.Char('Model Year',help='Year of the model')
    doors = fields.Integer('Doors Number', help='Number of doors of the vehicle', default=5)
    tag_ids = fields.Many2many('vehicle.tag', 'vehicle_vehicle_tag_rel', 'vehicle_tag_id', 'tag_id', 'Tags', copy=False)
    transmission = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic')], 'Transmission', help='Transmission Used by the vehicle')
    fuel_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
        ], 'Fuel Type', help='Fuel Used by the vehicle')
    horsepower = fields.Integer()
    horsepower_tax = fields.Float('Horsepower Taxation')
    power = fields.Integer('Power', help='Power in kW of the vehicle')
    co2 = fields.Float('CO2 Emissions', help='CO2 emissions of the vehicle')
    image_model = fields.Binary(related='model_id.image', string="Logo", readonly=False)
    image_medium = fields.Binary(related='model_id.image_medium', string="Logo (medium)", readonly=False)
    image_small = fields.Binary(related='model_id.image_small', string="Logo (small)", readonly=False)

    @api.depends('model_id.name')
    def _compute_vehicle_name(self):
        for record in self:
            record.name = record.model_id.name

 #######################################################################################################################################
    # @api.depends('model_id.brand_id.name', 'model_id.name', 'license_plate')
    # def _compute_vehicle_name(self):
    #     for record in self:
    #         record.name = record.model_id.brand_id.name + '/' + record.model_id.name + '/' + (
    #                     record.license_plate or _('No Plate'))

 ####################################################################################################################################
    @api.onchange('model_id')
    def _brand_onchange(self):
        list = []
        for rec in self.model_id.car_name:
            list.append(rec.id)
        return {'domain': {'car_name1': [('id', '=', list)]}}
    ##################################################################################################################################
    @api.onchange('model_id')
    def _onchange_model(self):
        if self.model_id:
            self.image_model = self.model_id.image_model
        else:
            self.image_model = False

    ##################################################################################################################################
    @api.one
    @api.constrains('license_plate')
    def unique_plateeidentity(self):
        if self.license_plate:
            identities = self.env['vehicle'].search_count([('license_plate', '=', self.license_plate)])
            if identities > 1:
                raise ValueError(_('This Plate number No. is already exist'))
    ###################################################################################################################################

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = args or []
        domain = expression.AND([domain, [('name', operator, name)]])
        # we don't want to override the domain's filter on driver_id if present
        if not any(['driver_id' in element for element in domain]):
            partner_ids = self.env['res.partner']._search([('name', operator, name)], access_rights_uid=name_get_uid)
            if partner_ids:
                domain = expression.OR([domain, ['|', ('driver_id', 'in', partner_ids), ('driver_id', '=', False)]])
        rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(rec).name_get()

    @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id('vehicle', xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('vehicle_id', '=', self.id)]
            )
            return res
        return False


    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'driver_id' in init_values:
            return 'vehicle.mt_fleet_driver_updated'
        return super(FleetVehicle, self)._track_subtype(init_values)

    def open_assignation_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignation Logs',
            'view_mode': 'tree',
            'res_model': 'vehicle.vehicle.assignation.log',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_driver_id': self.driver_id.id, 'default_vehicle_id': self.id}
        }




class FleetVehicleTag(models.Model):
    _name = 'vehicle.tag'
    _description = 'Vehicle Tag'

    name = fields.Char(required=True, translate=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [('name_uniq', 'unique (name)', "Tag name already exists !")]

