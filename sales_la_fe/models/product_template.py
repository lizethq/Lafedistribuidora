# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied
from odoo.tools.float_utils import float_round
from datetime import timedelta, time


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rack = fields.Char('Rack')
    file = fields.Char('Fila')
    case = fields.Char('Caso')

    purchase_product_qty=fields.Float(compute="_compute_purchase_product_qty",string='Purchased')
    sales_counts = fields.Float(compute='_compute_sales_counts', string='Sold')

    @api.depends('product_variant_ids.sales_counts')
    def _compute_sales_counts(self):
        for product in self:
            product.sales_counts = float_round(sum([p.sales_counts for p in product.with_context(active_test=False).product_variant_ids]), precision_rounding=product.uom_id.rounding)


    def _compute_purchase_product_qty(self):
        for template in self:
            template.purchase_product_qty = float_round(sum([p.purchase_product_qty for p in template.product_variant_ids]), precision_rounding=template.uom_id.rounding)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_product_qty=fields.Float(compute="_compute_purchase_product_qty",string='Purchased')
    sales_counts = fields.Float(compute='_compute_sales_counts', string='Sold')

    def _compute_sales_counts(self):
        r = {}
        self.sales_counts = 0
        if not self.user_has_groups('sales_team.group_sale_salesman'):
            return r
        date_from = fields.Datetime.to_string(fields.datetime.combine(fields.datetime.now() - timedelta(days=365),
                                                                      time.min))

        domain = [
            ('state', 'in', ['waiting', 'confirmed','partially_available','assigned']),
            ('picking_code','=','outgoing'),
            ('product_id', 'in', self.ids),
            ('date_expected', '>', date_from)
        ]
        for group in self.env['stock.move'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id']):
            r[group['product_id'][0]] = group['product_uom_qty']
        for product in self:
            if not product.id:
                product.sales_counts = 0.0
                continue
            product.sales_counts = float_round(r.get(product.id, 0), precision_rounding=product.uom_id.rounding)
        return r

    def _compute_purchase_product_qty(self):
        date_from = fields.Datetime.to_string(fields.datetime.now() - timedelta(days=365))
        domain = [
            ('state', 'in', ['waiting', 'confirmed','partially_available','assigned']),
            ('picking_code','=','incoming'),
            ('product_id', 'in', self.ids),
            ('date_expected', '>', date_from)
        ]
        PurchaseOrderLines = self.env['stock.move'].search(domain)
        order_lines = self.env['stock.move'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id'])
        purchased_data = dict([(data['product_id'][0], data['product_uom_qty']) for data in order_lines])
        for product in self:
            if not product.id:
                product.purchase_product_qty = 0.0
                continue
            product.purchase_product_qty = float_round(purchased_data.get(product.id, 0), precision_rounding=product.uom_id.rounding)
