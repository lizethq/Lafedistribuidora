# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # pricelist_item_ids = fields.Many2many('product.pricelist.item', 'Pricelist Items', compute='_get_pricelist_items')

    final_pricelist_item_ids = fields.One2many(
        'final.product.pricelist.item', 'product_tmpl_id', compute='_get_pricelist_items_price')

    # pricelist_name = fields.Char('Pricelist Name', compute='_get_pricelist_items_price')
    
    def _get_pricelist_items_price(self):
        product_obj = self.env['product.product']
        fppi_obj = self.env['final.product.pricelist.item']
        for record in self:
            product_ids = product_obj.search([('product_tmpl_id','=', record.id)])
            product_ids._get_pricelist_items()
            product_ids._get_pricelist_items_price()
            product_ids.flush(['pricelist_item_ids', 'final_pricelist_item_ids', 'pricelist_name'])
            fppi_ids = fppi_obj.search([('product_id','in',product_ids.ids)]).ids
            record.final_pricelist_item_ids = [(6,0,fppi_ids)]
            