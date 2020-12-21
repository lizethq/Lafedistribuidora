# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    amount_product = fields.Float('Cantidades:', compute='_compute_amount_products')
    total_products_fe = fields.Integer('Total productos:', compute='_compute_amount_products')
    
    @api.depends('order_line.product_qty')
    def _compute_amount_products(self):
        _logger.error('***************helloeveryone***************************')
        for record in self:
            _logger.error('***************helloeveryone***************************')
            if len(record.order_line) > 0:
                record.total_products_fe = len(record.order_line)
                record.amount_product = sum(record.order_line.mapped('product_qty'))
                _logger.error(record.amount_product)
            else:
                record.amount_product = False 
                record.total_products_fe = False 
                
                
    
        
    
    