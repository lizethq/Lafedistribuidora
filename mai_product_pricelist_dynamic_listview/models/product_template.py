# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # pricelist_item_ids = fields.Many2many('product.pricelist.item', 'Pricelist Items', compute='_get_pricelist_items')

    final_pricelist_item_ids = fields.One2many(
        'final.product.pricelist.item', 'product_tmpl_id') # compute='_get_pricelist_items_price')

    # pricelist_name = fields.Char('Pricelist Name', compute='_get_pricelist_items_price')