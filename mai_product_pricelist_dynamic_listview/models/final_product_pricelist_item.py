# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductPricelistItem(models.Model):
    _name = 'final.product.pricelist.item'
    _description = 'Final Product Pricelist Item'
    _rec_name = "pricelist_item_id"

    pricelist_id = fields.Many2one('product.pricelist')
    pricelist_item_id = fields.Many2one('product.pricelist.item')
    label = fields.Char('Discount')
    final_price = fields.Float('Price')
    product_id =  fields.Many2one('product.product')
    # product_tmpl_id =  fields.Many2one('product.template', string='Producto', compute='_get_product_tmpl_id')

    # def _get_product_tmpl_id(self):
    #     for rec in self:
    #         if rec.product_id:
    #             rec.product_tmpl_id = rec.product_id.product_tmpl_id.id
    #         else:
    #             rec.product_tmpl_id = False