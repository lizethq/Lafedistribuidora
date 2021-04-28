#Luis Felipe Paternina
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError
import base64

import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'


    pricelist_item_ids = fields.Many2many(
        'product.pricelist.item', 'Pricelist Items', compute='_get_pricelist_items')

    _sql_constraints = [
        ('barcode_uniq', 'unique(barcode)', _("A barcode can only be assigned to one product !")),
    ]




    def _get_pricelist_items(self):
        self.pricelist_item_ids = self.env['product.pricelist.item'].search([
            '|',
            ('product_id', '=', self.id),
            ('product_tmpl_id', '=', self.product_tmpl_id.id)]).ids


   