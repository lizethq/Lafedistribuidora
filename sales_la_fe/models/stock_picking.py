
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):

    _inherit = "stock.picking"

    note_sale = fields.Text('Nota de Cotización', related="sale_id.note")
    
