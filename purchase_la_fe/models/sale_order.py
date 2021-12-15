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
    int_pricelist = fields.Integer('Entero lista de precios', compute='_compute_check_pricelist')

    @api.depends('order_line.qty_delivered')
    def _compute_delivery_percentage(self):
        for record in self:
            if len(record.order_line) > 0:
                record.delivery_percentage =  (sum(record.order_line.mapped('qty_delivered')) * 100)/(record.amount_product or 1.0)
                record.test = (sum(record.order_line.mapped('qty_delivered')))
                record.invoice_percentage = (sum(record.order_line.mapped('qty_invoiced')) * 100)/(record.amount_product or 1.0)
            else:
                record.delivery_percentage = 0.0
                record.test = 0.0
                record.invoice_percentage = 0.0

    @api.depends('order_line.product_uom_qty')
    def _compute_amount_products(self):
        for record in self:
            if len(record.order_line) > 0:
                record.total_products_fe = len(record.order_line)
                record.amount_product = sum(record.order_line.mapped('product_uom_qty'))
                # _logger.error(record.amount_product)
            else:
                record.amount_product = False
                record.total_products_fe = False

    @api.depends('order_line.product_uom_qty')
    def _compute_check_sales_control_b(self):
        for record in self:
            for line in record.order_line:
                if line.product_id:
                    self.check_sales_control = True
                else:
                    self.check_sales_control = True

    @api.onchange('pricelist_id')
    def _compute_check_pricelist(self):
        for record in self:
            if len(record.pricelist_id):
                record.int_pricelist = record.pricelist_id.id
                if len(record.order_line)> 0:
                    pricelistitem_object = self.env['product.pricelist.item'].search([('pricelist_id', '=',record.int_pricelist )])
                    for i in pricelistitem_object:
                        for j in record.order_line:
                            if j.product_id.id == i.product_tmpl_id.id:
                                j.price_unit = i.fixed_price
                else:
                    record.int_pricelist = 0
            else:
                record.int_pricelist = 0
