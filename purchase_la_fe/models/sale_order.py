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
    check_sales_control = fields.Boolean('Cequear control de ventas', compute='_compute_check_sales_control_b')
    #check_pricelist = fields.Float('Chequear lista de proecios', compute= '')
    int_pricelist = fields.Integer('Entero lista de precios', compute='_compute_check_pricelist')
    
    @api.depends('order_line.qty_delivered')
    def _compute_delivery_percentage(self):
        # _logger.error('***************helloeveryone***************************')
        for record in self:
            # _logger.error('***************helloeveryone***************************')
            if len(record.order_line) > 0:
                # _logger.error('***************helloeveryonenight***************************')
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
        # _logger.error('***************helloeveryone***************************')
        for record in self:
            # _logger.error('***************helloeveryone***************************')
            if len(record.order_line) > 0:
                record.total_products_fe = len(record.order_line)
                record.amount_product = sum(record.order_line.mapped('product_uom_qty'))
                # _logger.error(record.amount_product)
            else:
                record.amount_product = False 
                record.total_products_fe = False 

    @api.depends('order_line.product_uom_qty')
    def _compute_check_sales_control_b(self):
        # logger.error('23/12/2020*********************')
        for record in self:
            for line in record.order_line:
                # _logger.error('******************23/12/2020*********************')
                if line.product_id:
                    self.check_sales_control = True
                    # _logger.error('**********23/12/2020')
                    # _logger.error(self.check_sales_control)
                else:
                    self.check_sales_control = True
                    
    @api.onchange('pricelist_id')
    def _compute_check_pricelist(self):
        for record in self:
            if len(record.pricelist_id):
                record.int_pricelist = record.pricelist_id.id
                if len(record.order_line)> 0:
                    # _logger.error('**********23/12/2020late')
                    pricelistitem_object = self.env['product.pricelist.item'].search([('pricelist_id', '=',record.int_pricelist )])
                    # #order_lines = self.env['sale.order.line'].search([('order_id', '=',self.id )])
                    # _logger.error(pricelistitem_object)
                    for i in pricelistitem_object:
                        for j in record.order_line:
                            # _logger.error(j.price_unit)
                            # _logger.error(i.fixed_price)
                            if j.product_id.id == i.product_tmpl_id.id:
                                # _logger.error('**********23/12/2020latehello************')
                                j.price_unit = i.fixed_price
                                # _logger.error(j.price_unit)
                                # _logger.error(i.fixed_price)
                            
                else:
                    record.int_pricelist = 0 
            else:
                record.int_pricelist = 0
                