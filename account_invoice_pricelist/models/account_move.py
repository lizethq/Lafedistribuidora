# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime
from pytz import timezone
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang, format_date, get_lang

logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Pricelist",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    
    
    """
    def action_post(self):
        logger.info('**********************************************0')
        if self.invoice_origin:
            for record in self:
                lot_line = self.env['stock.picking'].search([('origin','=',record.invoice_origin)])
                if lot_line:
                    for lines_account in record.invoice_line_ids:
                        for lines_picking in lot_line.move_line_ids_without_package.filtered(lambda x: x.product_id == lines_account.product_id and x.qty_done == lines_account.quantity):
                            logger.info(lines_picking.lot_id.id)
                            logger.info('**********************************************')
                            lines_account.sudo().update({'lot_id':lines_picking.lot_id.id})
                
        result = super(AccountMove, self).action_post()
        return result
    """
    
    
    @api.constrains("pricelist_id", "currency_id")
    def _check_currency(self):
        for sel in self.filtered(lambda a: a.pricelist_id and a.is_invoice()):
            if sel.pricelist_id.currency_id != sel.currency_id:
                raise UserError(
                    _("Pricelist and Invoice need to use the same currency.")
                )

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id_account_invoice_pricelist(self):
        if self.is_invoice():
            result = super(AccountMove, self)._onchange_partner_id()
            if (
                self.partner_id
                and self.type in ("out_invoice", "out_refund")
                and self.partner_id.property_product_pricelist
            ):
                self.pricelist_id = self.partner_id.property_product_pricelist
                self._set_pricelist_currency()
            return result

    @api.onchange("pricelist_id")
    def _set_pricelist_currency(self):
        if (
            self.is_invoice()
            and self.pricelist_id
            and self.currency_id != self.pricelist_id.currency_id
        ):
            self.currency_id = self.pricelist_id.currency_id

    def button_update_prices_from_pricelist(self):
        for inv in self.filtered(lambda r: r.state == "draft"):
            inv.invoice_line_ids._onchange_product_id_account_invoice_pricelist()
        self.filtered(lambda r: r.state == "draft").with_context(
            check_move_validity=False
        )._move_autocomplete_invoice_lines_values()
        self.filtered(lambda r: r.state == "draft").with_context(
            check_move_validity=False
        )._recompute_tax_lines()

    def _reverse_move_vals(self, default_values, cancel=True):
        move_vals = super(AccountMove, self)._reverse_move_vals(
            default_values, cancel=cancel
        )
        if self.pricelist_id:
            move_vals["pricelist_id"] = self.pricelist_id.id
        return move_vals


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    #lot_id = fields.Char(string='Lote/N° de Serie', compute="_compute_lot_id")
    #life_date = fields.Char(string='Fecha Venc. Lote', compute="_compute_lot_id")
    lot_id = fields.Char(string='Lote/N° de Serie')
    life_date = fields.Char(string='Fecha Venc. Lote')
    
    
    
    def write(self, values):
        res = super(AccountMoveLine, self).write(values)
        if 'lot_id' not in values and 'life_date' not in values:
            acumulador = 0
            sum_lot = 0
            residue = 0
            for line in self.move_id.invoice_line_ids.filtered(lambda line: line.exclude_from_invoice_tab is False):
                lot_id = []
                life_date = []
                if line.move_id.invoice_origin:
                    logger.error(line)
                    invoice_origin = line.move_id.invoice_origin.split(', ')
                    pickings = self.env['stock.picking'].search([('origin','in',invoice_origin)])
                    
                    if residue:
                        """ El residuo se resta a la suma total de cantidades de lote """
                        sum_lot -= residue
                    
                    local_sum = 0
                    for lines_picking in pickings.mapped('move_line_ids_without_package').filtered(lambda x: x.product_id == line.product_id):
                        sum_lot += lines_picking.qty_done
                        local_sum += lines_picking.qty_done
                        logger.error('Cantidad del lote: %s' % (lines_picking.qty_done))
                        logger.error('suma de lotes: %s' % (sum_lot))
                        logger.error('Acumulador: %s' % (acumulador))
                        logger.error('Residuo: %s' % (residue))
                        logger.error('cantidad de la linea evaluada: %s' % (line.quantity))
                        logger.error('Suma lotes local: %s' % (local_sum))
                        #logger.error(acumulador)
                        if local_sum > acumulador and local_sum <= acumulador + line.quantity:
                            """ Cuando la sumatoria de cantidad de lotes recorrtido esta en el rango de cantidades de linea de factura """
                            if residue:
                                lot_id.append((lines_picking.lot_id.name or '') + ' [' + str(residue) + ']')
                            else:
                                lot_id.append((lines_picking.lot_id.name or '') + ' [' + str(lines_picking.qty_done) + ']')
                            if lines_picking.lot_id.use_date:
                                life_date.append((str(lines_picking.lot_id.use_date.date()) or ''))
                            residue = 0
                            
                        elif local_sum > acumulador:
                            """ Cuando solo se debe poner una cantidad menor a lo que trae lote """
                            if (acumulador + line.quantity) - (sum_lot - lines_picking.qty_done) > 0:
                                lot_id.append((lines_picking.lot_id.name or '') + ' [' + str((acumulador + line.quantity) - (sum_lot - lines_picking.qty_done)) + ']')
                                if lines_picking.lot_id.use_date:
                                    life_date.append((str(lines_picking.lot_id.use_date.date()) or ''))
                                residue = sum_lot - (acumulador + line.quantity)
                                break
                        else:
                            logger.error('**********paso2')                        
                            #break
    
                    acumulador += line.quantity  
                    

            
            #if line.move_id.invoice_origin:
            #    invoice_origin = rec.move_id.invoice_origin.split(', ')
                #logger.error('******************++++++++++****************+RRRRRRRRR')    pickings = self.env['stock.picking'].search([('origin','in',invoice_origin)])
                #logger.error('******************++++++++++****************+RRRRRRRRR')    pickings = self.env['stock.picking'].search([('origin','in',invoice_origin)])
                line.lot_id = str(lot_id)
                line.life_date = str(life_date)
        return res
        
    

    @api.depends('move_id.invoice_line_ids')
    def _compute_lot_id(self):
        logger.info("\n\n\nel compute se calcula por cada linea de la factura")
        lot_id = []
        
        acumulador = 0
        #logger.error(self.filtered(lambda line: line.exclude_from_invoice_tab is False))
        #logger.error(len(self.filtered(lambda line: line.exclude_from_invoice_tab is False)))
    
        for rec in self:
            rec.lot_id = ''
            rec.life_date = ''
    
        for rec in self.filtered(lambda line: line.exclude_from_invoice_tab is False):
            logger.error("****************** recorriendo cada line de factura *****************")
            logger.error(rec)
            
            if rec.move_id.invoice_origin:
                logger.error("****************** entranda al if de origin")
                invoice_origin = rec.move_id.invoice_origin.split(', ')
                logger.error(invoice_origin)
                pickings = self.env['stock.picking'].search([('origin','in',invoice_origin)])
                #logger.error(pickings.mapped('move_line_ids_without_package').filtered(lambda x: x.product_id == rec.product_id))
                logger.error(pickings)
                for lines_picking in pickings.mapped('move_line_ids_without_package').filtered(lambda x: x.product_id == rec.product_id):
                    logger.error("****************** entrando al linea de picking")
                
                """
                
                sum_lot = 0
                logger.error(sum_lot)
                
                
                for lines_picking in pickings.mapped('move_line_ids_without_package').filtered(lambda x: x.product_id == rec.product_id):
                    sum_lot += lines_picking.qty_done
                    #logger.error(lines_picking.qty_done)
                    #logger.error(sum_lot)
                    logger.error("****************** recorriendo cada linea de picking *****************")
                    
                    
                    #logger.error(acumulador)
                    #logger.error(rec.quantity)
                    if sum_lot > acumulador and sum_lot <= acumulador + rec.quantity:
                        lot_id.append((lines_picking.lot_id.name or '') + ' [' + str(lines_picking.qty_done) + ']')
                    else:
                        lot_id.append((lines_picking.lot_id.name or '') + ' [' + str(rec.quantity) + ']')
                """
            acumulador += rec.quantity    
                
    
                            
                            
                            
            rec.lot_id = str(lot_id)
            rec.life_date = ',\n'


            
        
        
        
        """
        for record in self:
            logger.error("****************** recorriendo record *****************")
            lot_id = []
            life_date = []
            if record.move_id:
                #logger.info("******************1*************")
                items_invoices_number = len(record.move_id.invoice_line_ids)
                
                if record.move_id.invoice_origin:
                    #logger.info("******************2*************")
                    invoice_origin = record.move_id.invoice_origin.split(', ')
                    pickings = self.env['stock.picking'].search([('origin','in',invoice_origin)])
                    
                            
                    acumulador = 0
                    for line_invoices in self.move_id.invoice_line_ids:
                        logger.error("****************** recorriendo cada line a de factura *****************")
                        logger.error(record)
                        logger.error(line_invoices)
                        if line_invoices == self:
                            #logger.info("******************encontrada linea de la factura a tratar *****************")
                            #logger.info(self)
                            acumulador2 = 0
                            for lines_picking in pickings.mapped('move_line_ids_without_package').filtered(lambda x: x.product_id == record.product_id):
                                acumulador2 = lines_picking.qty_done
                                if acumulador2 > acumulador and acumulador2<= (acumulador + line_invoices.quantity):
                                    #logger.info("PICKINGS GENERADOS*************")
                                    #logger.info(lines_picking.lot_id.name)
                                    lot_id.append((lines_picking.lot_id.name or '') + ' [' + str(lines_picking.qty_done) + ']')
                                
                        acumulador += line_invoices.quantity
                        
                                        
                record.lot_id = str(lot_id)
                record.life_date = ',\n'
        """
            
        
    @api.onchange("product_id", "quantity")
    def _onchange_product_id_account_invoice_pricelist(self):
        for sel in self:
            if not sel.move_id.pricelist_id:
                return
            sel.with_context(check_move_validity=False).update(
                {"price_unit": sel._get_price_with_pricelist()}
            )

    @api.onchange("product_uom_id")
    def _onchange_uom_id(self):
        for sel in self:
            if (
                sel.move_id.is_invoice()
                and sel.move_id.state == "draft"
                and sel.move_id.pricelist_id
            ):
                price_unit = sel._get_computed_price_unit()
                taxes = sel._get_computed_taxes()
                if taxes and sel.move_id.fiscal_position_id:
                    price_subtotal = sel._get_price_total_and_subtotal(
                        price_unit=price_unit, taxes=taxes
                    )["price_subtotal"]
                    accounting_vals = sel._get_fields_onchange_subtotal(
                        price_subtotal=price_subtotal,
                        currency=self.move_id.company_currency_id,
                    )
                    balance = accounting_vals["debit"] - accounting_vals["credit"]
                    price_unit = sel._get_fields_onchange_balance(balance=balance).get(
                        "price_unit", price_unit
                    )
                sel.with_context(check_move_validity=False).update(
                    {"price_unit": price_unit}
                )
            else:
                super(AccountMoveLine, self)._onchange_uom_id()

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        PricelistItem = self.env["product.pricelist.item"]
        field_name = "lst_price"
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            while (
                pricelist_item.base == "pricelist"
                and pricelist_item.base_pricelist_id
                and pricelist_item.base_pricelist_id.discount_policy
                == "without_discount"
            ):
                price, rule_id = pricelist_item.base_pricelist_id.with_context(
                    uom=uom.id
                ).get_product_price_rule(product, qty, self.order_id.partner_id)
                pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == "standard_price":
                field_name = "standard_price"
                product_currency = product.cost_currency_id
            elif (
                pricelist_item.base == "pricelist" and pricelist_item.base_pricelist_id
            ):
                field_name = "price"
                product = product.with_context(
                    pricelist=pricelist_item.base_pricelist_id.id
                )
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(
                    product_currency,
                    currency_id,
                    self.company_id or self.env.company,
                    self.move_id.invoice_date or fields.Date.today(),
                )

        product_uom = self.env.context.get("uom") or product.uom_id.id
        if uom and uom.id != product_uom:
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    def _calculate_discount(self, base_price, final_price):
        discount = (base_price - final_price) / base_price * 100
        if (discount < 0 and base_price > 0) or (discount > 0 and base_price < 0):
            discount = 0.0
        return discount

    def _get_price_with_pricelist(self):
        price_unit = 0.0
        if self.move_id.pricelist_id and self.product_id and self.move_id.is_invoice():
            if self.move_id.pricelist_id.discount_policy == "with_discount":
                product = self.product_id.with_context(
                    lang=self.move_id.partner_id.lang,
                    partner=self.move_id.partner_id.id,
                    quantity=self.quantity,
                    date_order=self.move_id.invoice_date,
                    pricelist=self.move_id.pricelist_id.id,
                    product_uom_id=self.product_uom_id.id,
                    fiscal_position=(
                        self.move_id.partner_id.property_account_position_id.id
                    ),
                )
                tax_obj = self.env["account.tax"]
                recalculated_price_unit = (
                    product.price * self.product_id.uom_id.factor
                ) / (self.product_uom_id.factor or 1.0)
                price_unit = tax_obj._fix_tax_included_price_company(
                    recalculated_price_unit,
                    product.taxes_id,
                    self.tax_ids,
                    self.company_id,
                )
                self.with_context(check_move_validity=False).discount = 0.0
            else:
                product_context = dict(
                    self.env.context,
                    partner_id=self.move_id.partner_id.id,
                    date=self.move_id.invoice_date or fields.Date.today(),
                    uom=self.product_uom_id.id,
                )
                final_price, rule_id = self.move_id.pricelist_id.with_context(
                    product_context
                ).get_product_price_rule(
                    self.product_id, self.quantity or 1.0, self.move_id.partner_id
                )
                base_price, currency = self.with_context(
                    product_context
                )._get_real_price_currency(
                    self.product_id,
                    rule_id,
                    self.quantity,
                    self.product_uom_id,
                    self.move_id.pricelist_id.id,
                )
                if currency != self.move_id.pricelist_id.currency_id:
                    base_price = currency._convert(
                        base_price,
                        self.move_id.pricelist_id.currency_id,
                        self.move_id.company_id or self.env.company,
                        self.move_id.invoice_date or fields.Date.today(),
                    )
                price_unit = max(base_price, final_price)
                self.with_context(
                    check_move_validity=False
                ).discount = self._calculate_discount(base_price, final_price)
        return price_unit

    def _get_computed_price_unit(self):
        price_unit = super(AccountMoveLine, self)._get_computed_price_unit()
        if self.move_id.pricelist_id and self.move_id.is_invoice():
            price_unit = self._get_price_with_pricelist()
        return price_unit
