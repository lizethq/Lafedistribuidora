# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import AccessDenied
from collections import defaultdict
from odoo.exceptions import ValidationError
from odoo import fields, models
from odoo.tools import float_is_zero

logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    method_la_fe_id = fields.Many2one('payment.methods.la.fe', string='Forma de pago',compute='_compute_method_la_fe_id' )
    delivery_adress_shipping = fields.Char(
        'Domicilio de entrega', compute='_compute_partner_delivery_adress_shipping')
    zip_shipping_id = fields.Many2one(
        'res.city.zip', string='Ubicación zip entrega',compute='_compute_partner_delivery_zip_shipping')
    
    
    @api.onchange('partner_shipping_id')
    def _compute_partner_delivery_zip_shipping(self):
        for record in self:
            if record.partner_shipping_id:
                if record.partner_shipping_id.zip_id:
                    record.zip_shipping_id = record.partner_shipping_id.zip_id.id
                    logger.error('************hellos_2__2/08/2021**********')
                else:
                    record.zip_shipping_id = False
            else:
                record.zip_shipping_id = False
        return
    
    @api.onchange('partner_shipping_id')
    def _compute_partner_delivery_adress_shipping(self):
        for record in self:
            if record.partner_shipping_id:
                if record.partner_shipping_id.street:
                    record.delivery_adress_shipping = record.partner_shipping_id.street
                else:
                    record.delivery_adress_shipping = False
            else:
                record.delivery_adress_shipping = False
        return
    

    def _get_invoiced_lot_values(self):
        res = super(AccountMove, self)._get_invoiced_lot_values()
        for i in res:
            obje_lot = self.env['stock.production.lot'].search([('name','=', i['lot_name'])])
            logger.error('Hello everyone test 22/01/2021')
            logger.error(res)
            if len(obje_lot)>1:
                #raise ValidationError('Error')
                logger.error('Hello everyone test 22/01/2021 one')
                logger.error(obje_lot[0].use_date)
                i['use_date'] = obje_lot[0].use_date
            else:
                logger.error('Hello everyone test 22/01/2021 two')
                logger.error(obje_lot[0].use_date)
                i['use_date'] = obje_lot[0].use_date
        #lot_values = i
        logger.error('Hello everyone test 20')
        logger.error(res)
        return res

    
    
    @api.onchange('invoice_origin')
    def _compute_method_la_fe_id(self):
        for record in self:
            if record.invoice_origin:
                logger.error(record.invoice_origin)
                if len(record.invoice_origin)> 15:
                    logger.error('************Errorone***********')
                    list_a = []
                    str_one = ""
                    count = 0
                    for i in record.invoice_origin:
                        list_a.append(i)
                        str_one = str_one + i
                        count = count +1
                        if count == 15:
                            break
                    ab = str(list_a)
                    logger.error(ab)
                    logger.error(str_one)
                else:
                    str_one = record.invoice_origin   
                logger.error('************Errotwo***********')

                logger.error(str_one)
                sale_obj = self.env['sale.order'].search([('name','=',str_one)])
                logger.error('******helloVale********')
                logger.error(sale_obj)
                record.method_la_fe_id = sale_obj.method_la_fe_id.id
            else:
                record.method_la_fe_id = False

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    #new_expiration_date = fields.Date('Fecha de Vencimiento')
    x_cum = fields.Char('Código CUM', compute='_calculate_fields_product')
    x_invima = fields.Char('Código Invima', compute='_calculate_fields_product')
    x_atc = fields.Char('Código ATC', compute='_calculate_fields_product')
    removal_date = fields.Date('Fecha de vencimiento')

    def _sale_can_be_reinvoice(self):
        self.ensure_one()
        return not self.is_anglo_saxon_line and super(AccountMoveLine, self)._sale_can_be_reinvoice()


    def _stock_account_get_anglo_saxon_price_unit(self):
        self.ensure_one()
        price_unit = super(AccountMoveLine, self)._stock_account_get_anglo_saxon_price_unit()

        so_line = self.sale_line_ids and self.sale_line_ids[-1] or False
        if so_line:
            qty_to_invoice = self.product_uom_id._compute_quantity(self.quantity, self.product_id.uom_id)
            qty_invoiced = sum([x.product_uom_id._compute_quantity(x.quantity, x.product_id.uom_id) for x in so_line.invoice_lines if x.move_id.state == 'posted'])
            average_price_unit = self.product_id._compute_average_price(qty_invoiced, qty_to_invoice, so_line.move_ids)

            price_unit = average_price_unit or price_unit
            price_unit = self.product_id.uom_id._compute_price(price_unit, self.product_uom_id)
        return price_unit

    @api.onchange('product_id')
    def _calculate_fields_product(self):
        for record in self: 
            if record.product_id:
                obj_product = self.env['product.template'].search([('id','=',record.product_id.id)])
                logger.error(obj_product.id)
                #record.x_cum = record.product_id
                record.x_cum = obj_product.x_cum
                record.x_invima = obj_product.x_invima
                record.x_atc = obj_product.x_atc
                logger.error(record.x_cum)
                logger.error(record.x_invima)
                logger.error(record.x_atc)
                
            else:
                record.x_cum = False
                record.x_invima = False
                record.x_atc = False
                
    
                
            
                