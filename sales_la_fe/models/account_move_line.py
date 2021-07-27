# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"


    def write(self, vals):    
        user = self.env['res.users'].browse(self.env.uid)
        for line in self:
            if line.picking_id.state == 'done' and not user.has_group('base.group_system'):
                raise UserError("No puede cambiar valores de movimientos en un picking con estado terminado.")
        return super(StockMoveLine, self).write(vals)
