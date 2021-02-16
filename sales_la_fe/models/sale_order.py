# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import AccessDenied


logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    credit_aproved = fields.Char('Crédito aprobado?', compute='_compute_credit_aproved')
    method_la_fe_id = fields.Many2one('payment.methods.la.fe','Medios de pago')
    channel_id = fields.Many2one('channel.fe', 'Canal')
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", compute= '_compute_credit_aproved_two', store = True)
    
    check_credit_two = fields.Boolean('Check_two', compute='_compute_credit_aproved_two')
    street_sale_order = fields.Char('Domicilio de la compañía', compute='_compute_streets')
    #street2_sale_order = fields.Char('Dirección de entrega', compute='_compute_streets')
    
    zip = fields.Char('Dirección de entrega', compute='_compute_original_country_id')
    zip_id = fields.Many2one(
        'res.city.zip', string='Ubicación zip',compute='_compute_original_zip_id')
    state_id = fields.Many2one(
        'res.country.state', string=' ', compute='_compute_original_state_id')
    country_id = fields.Many2one(
        'res.country', string=' ', compute='_compute_original_country_id')
    #city = fields.Char('', )
    city_id = fields.Many2one(
        'res.city', string=' ', compute='_compute_original_country_id')
    delivery_adress = fields.Char(
        'Domicilio de entrega', compute='_compute_partner_delivery_adress')
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
    
    
    @api.onchange('partner_id')
    def _compute_partner_delivery_adress(self):
        for record in self:
            if record.partner_id:
                if record.partner_id.child_ids:
                    a = record.partner_id.child_ids.filtered(lambda x: x.type == 'delivery')
                    if len(a) > 0:
                        record.delivery_adress = a[0].street
                        logger.error('************hellos_2/08/2021**********')
                        logger.error(record.delivery_adress)
                    else:
                        record.delivery_adress = False
                else:
                    record.delivery_adress = False
            else:
                record.delivery_adress = False
                        
        return
    
    @api.onchange('partner_id')
    def _compute_original_country_id(self):
        for record in self:
            if record.partner_id:
                if record.partner_id.country_id:
                    record.country_id = record.partner_id.country_id.id
                    logger.error('************hellos2/02/2021**********')
                    logger.error(record.country_id)
                else:
                    record.country_id = False
            else:
                record.country_id = False           
        return
    
    @api.onchange('partner_id')
    def _compute_original_zip_id(self):
        for record in self:
            if record.partner_id:
                if record.partner_id.zip_id:
                    record.zip_id = record.partner_id.zip_id.id
                    record.zip = record.partner_id.zip_id.name
                    record.city_id = record.partner_id.zip_id.city_id.id
                    logger.error('************hellos2/02/2021**********')
                    logger.error(record.zip_id)
                else:
                    record.city_id = False
                    record.zip_id = False
                    record.zip = False
            else:
                record.city_id = False
                record.zip_id = False
                record.zip = False
        return
    
    @api.onchange('partner_id')
    def _compute_original_state_id(self):
        for record in self:
            if record.partner_id:
                if record.partner_id.state_id:
                    record.state_id = record.partner_id.state_id.id
                    logger.error('************hellos2/02/2021 II**********')
                    logger.error(record.state_id)
                else:
                    record.state_id = False
            else:
                record.state_id = False           
        return
    
    @api.onchange('partner_id')
    def _compute_streets(self):
        for record in self:
            if record.partner_id:
                if record.partner_id.street:
                    record.street_sale_order = record.partner_id.street
                else:
                    record.street_sale_order = False
                    #record.street2_sale_order = False
            else:
                record.street_sale_order = False
                #record.street2_sale_order = False
    
    
                    
                        
                
    
    @api.depends('partner_id')
    def _compute_credit_aproved(self):
        for record in self:
            if record.partner_id.study_credit:
                record.credit_aproved = record.partner_id.study_credit
            else:
                record.credit_aproved = False
                
    @api.depends('partner_id')
    def _compute_credit_aproved_two(self):
        for record in self:
            if record.partner_id.study_credit:
                if record.credit_aproved == 'No':
                    record.check_credit_two = True
                    if record.check_credit_two == True:
                        record.payment_term_id = 241
                    else:
                        record.payment_term_id.id = False
                else:
                    record.check_credit_two = False
                    record.credit_aproved = False
            else:
                record.credit_aproved = False
                record.check_credit_two = False
                    
    @api.onchange('pricelist_id')
    def _recompute_products_values(self):
        for record in self:
            for line in record.order_line:
                line.product_id_change()                   
                

    #new_expiration_date = fields.Date('Fecha de Vencimiento')