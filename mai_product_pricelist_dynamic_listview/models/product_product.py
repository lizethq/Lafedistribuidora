# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    pricelist_item_ids = fields.Many2many(
        'product.pricelist.item', 'Pricelist Items')

    final_pricelist_item_ids = fields.One2many(
        'final.product.pricelist.item', 'product_id')

    pricelist_name = fields.Char('Pricelist Name')
    
   
    