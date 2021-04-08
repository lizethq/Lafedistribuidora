from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"
    
    invima_code = fields.Char('Código Invima', compute="_compute_invima_code")
    
    @api.depends('product_id')
    def _compute_invima_code(self):
        for record in self:
            if record.product_id.x_invima:
                record.invima_code = record.product_id.x_invima
            else:
                record.invima_code = False
                
