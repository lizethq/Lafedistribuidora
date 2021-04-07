from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"
    
    invima_code = fields.Char('Código Invima', related="product_id.invima_code")
