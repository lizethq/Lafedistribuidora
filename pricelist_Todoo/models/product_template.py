#
#
# Todoo SAS
#
#
###################################################################################
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    item_ids = fields.One2many('product.template.pricelist', 'product_id', 'Lista de precios')

    