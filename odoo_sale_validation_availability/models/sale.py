# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_sale_ok(self):
        for record in self:
            if any([line <= 0 for line in record.order_line.mapped('quantity_on_hand')]):
                raise ValidationError("No se puede confirmar la orden por lineas de producto sin disponibilidad")

        return super(SaleOrder, self).action_sale_ok()

    def _action_confirm(self):
        for record in self:
            if any([line <= 0 for line in record.order_line.mapped('quantity_on_hand')]):
                raise ValidationError("No se puede confirmar la orden por lineas de producto sin disponibilidad")

        return super(SaleOrder, self)._action_confirm()



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    quantity_available = fields.Float(
        string="Cantidad Disponible"
    )
    quantity_on_hand = fields.Float(
        string="Cantidad a la Mano"
    )
    quantity_forecasted = fields.Float(
        string="Cantidad Proyectada"
    )
    qtty_available = fields.Float(
        string="Cantidad Disponible"
    )

    def _create_available_log(self):
        log = self.env['product.available.log']
        vals = []
        vals.append({
            'product_id': self.product_id.id,
            'sale_order_id': self.product_id.id,
            'user_id': self.env.user.id,
            'date': datetime.now(),
            'quantity_available': self.quantity_available,
            'quantity_on_hand': self.quantity_on_hand,
            'quantity_forecasted': self.quantity_forecasted,
            'product_uom_qty': self.product_uom_qty,
        })
        res = log.create(vals)
        return res

    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty_log(self):
        if self.product_uom_qty and self.product_id:
            self._create_available_log()

    @api.onchange('product_id')
    def _onchange_product_valid_avail(self):
        self.product_uom_qty = 0
        if self.product_id:
            self.quantity_on_hand = self.product_id.qty_available
            self.quantity_forecasted = self.product_id.virtual_available
            #self._create_available_log()


    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_available(self):
        if self.product_id:
            if self.order_id.state == 'draft':
                self.quantity_available = self.product_id.qty_available - self.product_uom_qty
                self.qtty_available = self.free_qty_today - self.product_uom_qty


    """Overwrite"""
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        vals.update(name=self.get_sale_order_line_multiline_description_sale(product))

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            company = self.company_id or self.order_id.company_id
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, company)
        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result
