# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import AccessDenied

logger = logging.getLogger(__name__)



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    #new_expiration_date = fields.Date('Fecha de Vencimiento')
    x_cum = fields.Char('Código CUM', compute='_calculate_fields_product')
    x_invima = fields.Char('Código Invima', compute='_calculate_fields_product')
    x_atc = fields.Char('Código ATC', compute='_calculate_fields_product')

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