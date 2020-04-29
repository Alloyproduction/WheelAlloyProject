from odoo import api, tools, fields, models, _
import base64
from odoo import modules
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
import datetime
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare



class ResSalesConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'


    No_of_hours = fields.Float(string="Hours for task" ,default=72)


    @api.model
    def get_values(self):
        res = super(ResSalesConfigSettings, self).get_values()
        config = self.env['ir.config_parameter'].sudo()
        no_hours=float(config.get_param('No_of_hours'))

        res.update(
            No_of_hours=no_hours,

        )
        return res

    @api.multi
    def set_values(self):
        res=super(ResSalesConfigSettings, self).set_values()
        config = self.env['ir.config_parameter'].sudo()
        config.set_param('No_of_hours',self.No_of_hours)

        # self.write({'maximum_amount_leader':self.maximum_amount_leader,'maximum_amount': self.maximum_amount})
        return res