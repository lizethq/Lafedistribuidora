# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_product = fields.Float('Cantidades:', compute='_compute_amount_products')
    total_products_fe = fields.Integer('Total productos:', compute='_compute_amount_products')
    delivery_percentage = fields.Float('Porcentaje de entrega', compute='_compute_delivery_percentage')
    invoice_percentage = fields.Float('Porcentaje facturado', compute='_compute_delivery_percentage')
    test = fields.Float('Porcentaje de entrega', compute='_compute_delivery_percentage')
    
    @api.depends('order_line.qty_delivered')
    def _compute_delivery_percentage(self):
        _logger.error('***************helloeveryone***************************')
        for record in self:
            _logger.error('***************helloeveryone***************************')
            if len(record.order_line) > 0:
                _logger.error('***************helloeveryonenight***************************')
                record.delivery_percentage =  (sum(record.order_line.mapped('qty_delivered')) * 100)/(record.amount_product)
                record.test = (sum(record.order_line.mapped('qty_delivered')))
                record.invoice_percentage = (sum(record.order_line.mapped('qty_invoiced')) * 100)/(record.amount_product)
                    #_logger.error(record.delivery_percentage)     
            else:
                record.delivery_percentage = 0.0
                record.test = 0.0
                record.invoice_percentage = 0.0
            
    
    @api.depends('order_line.product_uom_qty')
    def _compute_amount_products(self):
        _logger.error('***************helloeveryone***************************')
        for record in self:
            _logger.error('***************helloeveryone***************************')
            if len(record.order_line) > 0:
                record.total_products_fe = len(record.order_line)
                record.amount_product = sum(record.order_line.mapped('product_uom_qty'))
                _logger.error(record.amount_product)
            else:
                record.amount_product = False 
                record.total_products_fe = False 
    