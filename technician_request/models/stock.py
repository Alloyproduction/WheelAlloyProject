
from odoo import api, fields, models, _ , SUPERUSER_ID

class Picking(models.Model):

    _inherit = "product.product"

    # description =fields.Char("description",related="product_tmpl_id.description")