from odoo import models,fields,api
import logging
from itertools import chain
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError




logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    last_price1 = fields.Float('Ultimo precio(1)')
    last_price2 = fields.Float('Ultimo precio(2)')
    partner_id = fields.Many2one('res.patner')
    check_control_sales = fields.Boolean('')
    
    inventory_quantity = fields.Float('Cantidad a la mano', compute='_calculate_inventory_quantity')
    virtual_available = fields.Float('Cantidad proyectada', compute='_calculate_inventory_virtual')
    discount = fields.Float(string='Discount (%)',  default=0.0, digits=(12,2))
    #digits='Discount',
    @api.onchange('product_id')
    def calculate_the_last_two_prices(self):
        for record in self:
            if record.product_id:
                if record.order_id.partner_id.id:
                    sale_obj = []
                    sale_obj = self.env['sale.order'].search([('partner_id','=',record.order_id.partner_id.id)])
                    if len(sale_obj) > 0:   
                        a = len(sale_obj)
                        logger.error('*****hello27/12/2020first*********')
                        logger.error(a)
                        logger.error('*****hello27/12/2020second*********')
                        sale_lines = []
                        sale_obj_ids = []
                        for i in sale_obj:
                            sale_obj_ids.append(i.id)
                        for j in sale_obj_ids:
                            logger.error(j)
                        sale_order_lines = []
                        sale_order_lines = self.env['sale.order.line'].search([('order_id','in',sale_obj_ids),('product_id','=',record.product_id.id)])
                        if len(sale_order_lines) >= 2: 
                            #logger.error(sale_order_lines)
                            record.last_price1 = sale_order_lines[0].price_unit
                            record.last_price2 = sale_order_lines[1].price_unit
                        elif len(sale_order_lines) == 1:
                            record.last_price1 = sale_order_lines[0].price_unit
                            record.last_price2 = 0.0 
                        else:
                            record.last_price1 = 0.0
                            record.last_price2 = 0.0
                    else:
                        record.last_price1 = 0.0
                        record.last_price2 = 0.0 
                else:
                    record.last_price1 = 0.0
                    record.last_price2 = 0.0
            else:
                record.last_price1 = 0.0
                record.last_price2 = 0.0
                
    @api.onchange('product_id')
    def calculate_the_possible_products(self):
        for record in self:
            if record.product_id:
                #product_obj = self.env['product.product'].search([('id','=', record.product_id.id)])
                if record.product_id.x_control_ventas:
                    if record.order_id.partner_id.x_control_ventas:
                        logger.error('*****hello27/12/2020third*********')
                        logger.error(record.order_id.partner_id.x_control_ventas)
                        logger.error(record.product_id.x_control_ventas)
                        if record.order_id.partner_id.x_control_ventas == 'No' and record.product_id.x_control_ventas == 'Sí':
                            record.check_control_sales = True
                            raise ValidationError("Este producto no puede ser vendido a este cliente")
                        else:
                            record.check_control_sales  = False
                    else:
                        record.check_control_sales = False
                else:
                    record.check_control_sales = False
            else:
                record.check_control_sales = False
    
    @api.onchange('product_id')
    def _compute_amount_available(self):
        for record in self:
            if record.product_id:
                obj_product = record.product_id.qty_available
                logger.error('************27/01/2021***********')
                logger.error(obj_product)
                #"if obj_product != False:
                if obj_product  == 0.0 or obj_product  < 0.0:
                    raise ValidationError('No hay cantidades disponibles de este producto ')
                    #message_id = self.env['message.wizard'].create({'message': _("Invitation is successfully sent")})
                
                
    @api.onchange('product_id')
    def _calculate_inventory_quantity(self):
        for record in self:
            if record.product_id:
                #pro_obj = self.env['product.template'].search([('id','=',record.product_id.id)])
                if record.product_id.qty_available:
                    record.inventory_quantity = record.product_id.qty_available
                else:
                    record.inventory_quantity = 0.0
            else:
                record.inventory_quantity = 0.0
    
    @api.onchange('product_id')
    def _calculate_inventory_virtual(self):
        for record in self:
            if record.product_id:
                #pro_obj = self.env['product.template'].search([('id','=',record.product_id.id)])
                if record.product_id.virtual_available:
                    record.virtual_available = record.product_id.virtual_available
                else:
                    record.virtual_available = 0.0
            else:
                record.virtual_available = 0.0
                            
                    
        