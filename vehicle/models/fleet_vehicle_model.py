# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools

class FleetVehicleModel(models.Model):
    _name = 'vehicle.model'
    _description = 'Model of a vehicle'
    _order = 'name asc'

    name = fields.Char(required=True )
    active = fields.Boolean(default=True)
    image_model = fields.Binary("Logo", attachment=True,
                          help="This field holds the image used as logo for the car model, limited to 1024x1024px.")
    brand_id = fields.Many2one('vehicle.model.brand', 'Make', help='Make of the vehicle')
    image = fields.Binary(related='brand_id.image', string="Logo", readonly=False)
    image_medium = fields.Binary(related='brand_id.image_medium', string="Logo (medium)", readonly=False)
    image_small = fields.Binary(related='brand_id.image_small', string="Logo (small)", readonly=False)
    car_name = fields.Many2many(
        comodel_name='vehicle.name',
        relation='name',
        column1='name',
        column2='descrption',)

    # @api.multi
    # @api.depends('name', 'brand_id')
    # def name_get(self):
    #     res = []
    #     for record in self:
    #         name = record.name
    #         if record.brand_id.name:
    #             name = record.brand_id.name + '/' + name
    #         res.append((record.id, name))
    #     return res

    @api.onchange('brand_id')
    def _onchange_brand(self):
        if self.brand_id:
            self.image_medium = self.brand_id.image
        else:
            self.image_medium = False


class FleetVehicleModelBrand(models.Model):
    _name = 'vehicle.model.brand'
    _description = 'Brand of the vehicle'
    _order = 'name asc'

    name = fields.Char('Make', required=True)
    image = fields.Binary("Logo", attachment=True,
        help="This field holds the image used as logo for the brand, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized image", attachment=True,
        help="Medium-sized logo of the brand. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
        help="Small-sized logo of the brand. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            tools.image_resize_images(vals)
        return super(FleetVehicleModelBrand, self).create(vals_list)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(FleetVehicleModelBrand, self).write(vals)

    class Vehiclename(models.Model):
        _name = 'vehicle.name'
        _description = 'Name of a vehicle'
        _order = 'name asc'

        name = fields.Char('Car model')
        description = fields.Char('Description')
        image = fields.Binary("Logo", attachment=True,
                              help="This field holds the image used as logo for the Car, limited to 1024x1024px.")
        model_id = fields.Many2one('vehicle.model',
                                   track_visibility="onchange", required=True, help='Model of the vehicle')
        car_price = fields.Many2many(
            comodel_name='vehicle.price')
            # relation='name',
            # column1='name',
            # column2='description', )

        ######################################################################################################################

        class Vehicleprice(models.Model):
            _name = 'vehicle.price'
            _description = 'price of a vehicle'
            _order = 'name asc'

            @api.model
            def _get_default_name(self):
                return self.env['ir.sequence'].next_by_code('vehicle.price')

            name = fields.Char('Code', size=32, required=True, default=_get_default_name, track_visibility='onchange')
            repair_type = fields.Char('Repair Type')
            amount = fields.Float(string='Model Price', digits=(2, 2))
            description = fields.Char('Description')
            # car_name1 = fields.Many2one('vehicle.name', string='Car model',
            #                             track_visibility="onchange", required=True, help='Name of the vehicle')



