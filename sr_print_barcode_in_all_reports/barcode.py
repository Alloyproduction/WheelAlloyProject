from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp

class InheritclaimSale(models.Model):
    _inherit = 'sale.order'

    barcode = fields.Binary('product.product', string='barcode', related='product_id.barcode', store=True, readonly=False)

