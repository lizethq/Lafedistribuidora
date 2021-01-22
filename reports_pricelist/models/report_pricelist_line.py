# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportPricelistLine(models.Model):
    _name = 'report.pricelist.line'
    _description = 'Report pricelist line'
    
    report_id = fields.Many2one('report.pricelist', string='Report', index=True, ondelete='cascade', translate=True)
    pricelist_item_id = fields.Many2one('product.pricelist.item', string='Pricelist item', index=True,
                                        ondelete='cascade', translate=True)
    product_id = fields.Many2one('product.product', string='Product', index=True, ondelete='cascade')
    qty = fields.Float(string='Quantity', default=0)
