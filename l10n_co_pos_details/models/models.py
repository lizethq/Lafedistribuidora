# -*- coding: utf-8 -*-
from datetime import timedelta
import pytz
from odoo import api, fields, models, tools, _
import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.osv.expression import AND
import base64
_logger = logging.getLogger(__name__)

class PosOrderLine(models.Model):
    _name = "pos.order.line"
    _inherit = "pos.order.line"
    _description = "Point of Sale Order Lines"

    def _compute_tax_report(self):
        self.ensure_one()
        fpos = self.order_id.fiscal_position_id
        tax_ids_after_fiscal_position = fpos.map_tax(self.tax_ids, self.product_id, self.order_id.partner_id) if fpos else self.tax_ids
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = tax_ids_after_fiscal_position.compute_all(price, self.order_id.pricelist_id.currency_id, self.qty, product=self.product_id, partner=self.order_id.partner_id)
        iva19 = 0
        iva5 = 0
        exento = 0
        for data in taxes['taxes']:
            if data['name'] == 'IVA Ventas 19%':
                iva19 += data['amount']
            if data['name'] == 'IVA Ventas 5%':
                iva5 += data['amount']
            if data['name'] == 'IVA Excento':
                exento += exento + price

        return {
            'iva19': iva19,
            'iva5': iva5,
            'exento': exento,
        }



class PosSession(models.Model):
    _name = 'pos.session'
    _inherit = 'pos.session'

    def user_print(self):
        usuario = self.env['res.users'].browse(self._uid)
        return usuario.name

    def efectivo(self):
        total_cash_payment = 0
        for session in self:
            total_cash_payment = sum(session.order_ids.mapped('payment_ids').filtered(
                lambda payment: payment.payment_method_id.name == 'Efectivo').mapped('amount'))
        return total_cash_payment

    def bancolombia(self):
        total_cash_payment = 0
        for session in self:
            total_cash_payment = sum(session.order_ids.mapped('payment_ids').filtered(
                lambda payment: payment.payment_method_id.name == 'Bancolombia').mapped('amount'))
        return total_cash_payment

    def datafono(self):
        total_cash_payment = 0
        for session in self:
            total_cash_payment = sum(session.order_ids.mapped('payment_ids').filtered(
                lambda payment: payment.payment_method_id.name == 'Datafono').mapped('amount'))
        return total_cash_payment

    def credito(self):
        total_cash_payment = 0
        for session in self:
            total_cash_payment = sum(session.order_ids.mapped('payment_ids').filtered(
                lambda payment: payment.payment_method_id.name == 'Credito').mapped('amount'))
        return total_cash_payment
