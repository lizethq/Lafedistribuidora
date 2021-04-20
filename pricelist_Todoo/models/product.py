#Luis Felipe Paternina
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError
import base64

import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'


    quantity_tst = fields.Float(string='Cantidad por Ubicación TST', compute='_compute_value_svl_tst', search='_compute_qty_tst')
    
    def _compute_qty_tst(self, operator, value):
        recs = self.search([]).filtered(lambda x : x.quantity_tst > 0)
        if recs:
            return [('id', 'in', [x.id for x in recs])]
        """
        if value == 0.0 and operator == '>' and not ({'from_date', 'to_date'} & set(self.env.context.keys())):
            product_ids = self._search_qty_available_new(
                operator, value, self.env.context.get('lot_id'), self.env.context.get('owner_id'),
                self.env.context.get('package_id')
        """
    
    
    @api.depends('stock_valuation_layer_ids')
    @api.depends_context('to_date', 'force_company')
    def _compute_value_svl_tst(self):
        """Compute `value_svl` and `quantity_svl`."""
        _logger.error('******************************\n++++++++++++++++++++++++++++++')
        
        res = super(ProductProduct, self)._compute_value_svl()
        company_id = self.env.context.get('force_company', self.env.company.id)
        _logger.error(company_id)
        domain = [
            ('product_id', 'in', self.ids),
            ('company_id', '=', company_id),
        ]
        if self.env.context.get('to_date'):
            to_date = fields.Datetime.to_datetime(self.env.context['to_date'])
            domain.append(('create_date', '<=', to_date))
        
        warehouse_obj = self.env.user.warehouse_id
        warehouse_str = warehouse_obj.code + '/' + 'Existencias'
        _logger.error(warehouse_str)
        location_obj = self.env['stock.location'].search([('complete_name','ilike',warehouse_str)])
        _logger.error(location_obj)
        if warehouse_str:
            domain.append(('location_id', '=', location_obj.id))
        _logger.error(domain)      
        stock_quant = self.env['stock.quant'].search(domain)
        _logger.error(stock_quant)      
        products = self.browse()
        for quant in stock_quant:
            product = self.browse(quant.product_id.id)
            #product.value_svl = self.env.company.currency_id.round(group['value'])
            product.quantity_tst = quant.quantity
            products |= product
        remaining = (self - products)
        remaining.quantity_tst = 0
        
        return res
        