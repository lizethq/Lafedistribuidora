#Luis Felipe Paternina
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError
import base64

import logging

_logger = logging.getLogger(__name__)


class ProductTemplatePricelist(models.Model):
    _name = 'product.template.pricelist'


    product_id = fields.Many2one('product.template')
    pricelist_id = fields.Many2one('product.pricelist.item')
    price = fields.Float(string="Precio")
    min_qty = fields.Integer('Cantidad min.')
    start_date = fields.Date(string="Fecha de Inicio")
    end_date = fields.Date(string="Fecha de Final")
    sequence = fields.Integer()


   
        