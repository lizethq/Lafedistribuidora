# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields

class res_partner(models.Model):
    _inherit= 'res.partner'
    
    check_credit = fields.Boolean('Check Credit')
    credit_limit_on_hold  = fields.Boolean('Credit limit on hold')
    credit_limit = fields.Float('Credit Limit', tracking=True)
    property_product_pricelist = fields.Many2one(tracking=True)
    property_payment_term_id = fields.Many2one(tracking=True)
    user_id = fields.Many2one(tracking=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: