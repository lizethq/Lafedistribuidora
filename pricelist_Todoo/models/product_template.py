#
#
# Todoo SAS
#
#
###################################################################################
from odoo import models, fields, api, tools
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    item_ids = fields.One2many('product.pricelist.item', 'product_tmpl_id', 'Pricelist Items', compute="_get_products")
    
    pricelist_html = fields.Html('Campos html', compute="_compute_pricelist_html")
    

    
    @api.depends('item_ids')
    def _compute_pricelist_html(self):

        html = '<table class="table"><thead><tr><th scope="col">Lista de Precio</th><th scope="col">Precio</th></tr></thead><tbody>'
        for record in self.item_ids:
            html+='<tr><td>'
            html+= str(record.name)
            html+='</td>'
            html+='<td>'
            
            if record.base == 'list_price':
                price_limit = self.list_price
                price = self.list_price*(1-record.percent_price/100)  
            elif record.base == 'standard_price':
                price_limit = self.list_price
                price = self.list_price*(1-record.percent_price/100)
            else:
                price_limit = self.list_price
                price = self.list_price*(1-record.percent_price/100)
            

            if record.compute_price == 'fixed':
                html+= str('$ ')+str("{:,}".format(record.fixed_price).replace(',','~').replace('.',',').replace('~','.'))
            elif record.compute_price == 'percentage':
                html+= str('$ ')+str("{:,}".format(self.list_price*(1-record.percent_price/100)).replace(',','~').replace('.',',').replace('~','.'))
            else:
                _logger.info("****************************TEST ENTRADA**********************")
                _logger.info(record.price_surcharge)
                new_price = price-price*(record.price_discount/100)+record.price_surcharge
                if record.price_round > 0:
                    new_price = tools.float_round(new_price, precision_rounding= record.price_round) 
                
                price_format= '{:20,.2f}'.format(new_price)
                #html+= str(price_format)
                html+= str('$ ')+str("{:,}".format(new_price).replace(',','~').replace('.',',').replace('~','.'))

                
            html+='</td>'
            html+='</tr>'
            html+='</tr>'
            
            
        
        html += '</tbody></tr></table>'
        
        self.pricelist_html = html
            
    
    
    @api.depends('write_date')
    def _get_products(self):
        ids_product = []
        ids_list_price = []
        ids_price_product = []
        ids_price_global = []
        pricelist_product = self.env['product.pricelist.item'].search([('applied_on','=','3_global')]) 
        pricelist_global = self.env['product.pricelist.item'].search([('product_tmpl_id','=',self.id)])
        pricelist_category = self.env['product.pricelist.item'].search([('categ_id','=',self.categ_id.id)])
        pricelist_variant = self.env['product.pricelist.item'].search([('product_id','=',self.categ_id.id)])
        
        _logger.info("************************************ARRAY'S**************************+")
                
        for line_product in pricelist_global:
            if line_product.pricelist_id.active == True and line_product.pricelist_id.id not in ids_list_price:
                ids_product.append(line_product.id)
                ids_list_price.append(line_product.pricelist_id.id)
        
        for line_product in pricelist_category:
            if line_product.pricelist_id.active == True and line_product.pricelist_id.id not in ids_list_price:
                ids_product.append(line_product.id)
                ids_list_price.append(line_product.pricelist_id.id)
        
        for line_product in pricelist_product:
            if line_product.pricelist_id.active == True and line_product.pricelist_id.id not in ids_list_price:
                ids_product.append(line_product.id)
                ids_list_price.append(line_product.pricelist_id.id)


                    
        self.item_ids = [(6, 0, ids_product)]

        
