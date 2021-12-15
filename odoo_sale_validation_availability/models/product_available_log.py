# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductAvailableLog(models.Model):
    _name = 'product.available.log'
    _order = 'date desc'

    product_id = fields.Many2one('product.product', 'Producto', readonly=True)
    sale_order_id = fields.Many2one('product.product', 'Orden de Venta', readonly=True)
    user_id = fields.Many2one('res.users', 'Usuario', readonly=True)
    date = fields.Datetime('Fecha y Hora', readonly=True)
    quantity_available = fields.Float(
        string="Available Quantity", readonly=True
    )
    quantity_on_hand = fields.Float(
        string="Quantity On Hand", readonly=True
    )
    quantity_forecasted = fields.Float(
        string="Forecasted Quantity", readonly=True
    )
    product_uom_qty = fields.Float(
        string="Forecasted Quantity", readonly=True
    )
