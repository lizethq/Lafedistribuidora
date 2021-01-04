# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    credit_aproved = fields.Char('Crédito aprobado?', compute='_compute_credit_aproved')
    method_la_fe_id = fields.Many2one('payment.methods.la.fe','Medios de pago')
    channel_id = fields.Many2one('channel.fe', 'Canal')
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", compute= '_compute_credit_aproved_two', store = True)
    
    check_credit_two = fields.Boolean('Check_two', compute='_compute_credit_aproved_two')
    
    
    
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