# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    """ 
    product_uom = fields.Many2one('uom.uom')
    product_uom_qty = fields.Float(string="Cantidad")

    pricelist_item_ids = fields.Many2many(
        'product.pricelist.item', 'Pricelist Items', compute='_get_pricelist_items')

    final_pricelist_item_ids = fields.One2many(
        'final.product.pricelist.item', 'product_id', compute='_get_pricelist_items_price')

    pricelist_name = fields.Char('Pricelist Name', compute='_get_pricelist_items_price')



    def _get_display_price(self, product, pricelist_id, item_id):
        if pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.env.user.partner_id.id, date=fields.Datetime.now(), uom=self.product_uom.id)

        final_price, rule_id = pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.env.user.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, pricelist_id.id)
        if currency != pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, pricelist_id.currency_id, self.env.company, fields.Date.today())
        return max(base_price, final_price)



    def _get_pricelist_items_price(self):
        fppi_obj = self.env['final.product.pricelist.item']
        new_rec_list = []
        for rec in self:
            pricelist_name = []
            if not rec.pricelist_item_ids:
                rec.final_pricelist_item_ids = [(6,0, [])]
                rec.pricelist_name = ''
            else:    
                count = 1
                pricelist_list_check = []
                for new_rec in rec.pricelist_item_ids:
                    if new_rec.pricelist_id.name not in pricelist_name:
                        pricelist_name.append(new_rec.pricelist_id.name)
                    final_price = self._get_display_price(rec, new_rec.pricelist_id, new_rec)
                    new_fppi_id = fppi_obj.create({
                        'pricelist_id': new_rec.pricelist_id.id,
                        'label': new_rec.price,
                        'product_id': rec.id,
                        'final_price': final_price,
                        'pricelist_item_id': new_rec.id
                        })
                    
                    new_rec_list.append(new_fppi_id.id)
                    if new_rec.pricelist_id.id not in pricelist_list_check and new_rec.pricelist_id.allow_in_product_view:
                        name = 'x_pricelist_' + str(count)
                        field_id = self.env['ir.model.fields'].search([('model', '=', 'product.product'), ('name', '=', name)])
                        if field_id:
                            rec.write({name: new_rec.pricelist_id.name + ' - ' + str(round(final_price, 3))})
                        count += 1
                        pricelist_list_check.append(new_rec.pricelist_id.id)
                fppi_to_remove = fppi_obj.search([('product_id','=',rec.id),
                                                  ('id','not in',new_rec_list)]).ids
                if fppi_to_remove:
                    fppi_to_remove.append(0)
                    self._cr.execute("DELETE FROM final_product_pricelist_item where id in %s" % str(tuple(fppi_to_remove)))
                rec.final_pricelist_item_ids = new_rec_list
                rec.pricelist_name = ', '.join(pricelist_name)



    def _get_pricelist_items(self):
        ppi_obj = self.env['product.pricelist.item']
        for rec in self:
            pricelist_item_product_templ_ids = ppi_obj.search([
                '|',
                ('product_id', '=', rec.id),
                ('product_tmpl_id', '=', rec.product_tmpl_id.id),
                ('pricelist_id.allow_in_product_view', '=', True),
                ]).ids

            pricelist_item_global_ids = ppi_obj.search([
                ('applied_on', '=', '3_global'),
                ('pricelist_id.allow_in_product_view', '=', True),
                ]).ids

            pricelist_item_categ_ids = ppi_obj.search([
                ('applied_on', '=', '2_product_category'),
                ('pricelist_id.allow_in_product_view', '=', True),
                ('categ_id', '=', rec.categ_id.id)
                ]).ids

            final_list = pricelist_item_product_templ_ids + pricelist_item_global_ids + pricelist_item_categ_ids
            rec.pricelist_item_ids = [(6,0,final_list)] """