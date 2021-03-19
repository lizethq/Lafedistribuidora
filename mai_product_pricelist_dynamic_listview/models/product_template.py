# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # pricelist_item_ids = fields.Many2many('product.pricelist.item', 'Pricelist Items', compute='_get_pricelist_items')

    final_pricelist_item_ids = fields.One2many(
        'final.product.pricelist.item', 'product_tmpl_id', compute='_get_pricelist_items_price')

    # pricelist_name = fields.Char('Pricelist Name', compute='_get_pricelist_items_price')
    
    def _get_pricelist_items_price(self):
        product_obj = self.env['product.product']
        fppi_obj = self.env['final.product.pricelist.item']
        new_rec_list = []
        for record in self:
            product_ids = product_obj.search([('product_tmpl_id','=', record.id)])
            for rec in product_ids:
                pricelist_name = []
                rec._get_pricelist_items()
                if not rec.pricelist_item_ids:
                    rec.final_pricelist_item_ids = [(6,0, [])]
                    rec.pricelist_name = ''
                else:
                    for new_rec in rec.pricelist_item_ids:
                        if new_rec.pricelist_id.name not in pricelist_name:
                            pricelist_name.append(new_rec.pricelist_id.name)
                        final_price = rec._get_display_price(rec, new_rec.pricelist_id, new_rec)
                        new_fppi_id = fppi_obj.create({
                            'pricelist_id': new_rec.pricelist_id.id,
                            'label': new_rec.price,
                            'product_id': rec.id,
                            'product_tmpl_id': rec.product_tmpl_id.id,
                            'final_price': final_price,
                            'pricelist_item_id': new_rec.id
                            })
                        
                        new_rec_list.append(new_fppi_id.id)
                    fppi_to_remove = fppi_obj.search([('product_id','=',rec.id),
                                                    ('id','not in',new_rec_list)]).ids
                    if fppi_to_remove:
                        fppi_to_remove.append(0)
                        # self._cr.execute("DELETE FROM final_product_pricelist_item where id in %s" % str(tuple(fppi_to_remove)))
            record.final_pricelist_item_ids = new_rec_list