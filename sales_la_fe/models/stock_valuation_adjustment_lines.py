# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied


class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    cost_per_unit = fields.Float('Costo adicional por unidad', compute='_compute_cost_per_unit')
    
    @api.onchange('product_id')
    def _compute_cost_per_unit(self):
        for record in self:
            if record.additional_landed_cost and record.quantity:
                record.cost_per_unit = record.additional_landed_cost / record.quantity
            else:
                record.cost_per_unit = False
