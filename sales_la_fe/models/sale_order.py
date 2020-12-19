# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    credit_aproved = fields.Char('Crédito aprobado?', compute='_compute_credit_aproved')
    method_la_fe_id = fields.Many2one('payment.methods.la.fe','Medios de pago')
    
    @api.depends('partner_id')
    def _compute_credit_aproved(self):
        for record in self:
            if record.partner_id.study_credit:
                record.credit_aproved = record.partner_id.study_credit
            else:
                record.credit_aproved = False
                
                

    #new_expiration_date = fields.Date('Fecha de Vencimiento')