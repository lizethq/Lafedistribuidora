#Luis Felipe Paternina
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError
import base64

import logging

_logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'


    product_id = fields.Many2one('product.template')


   
        