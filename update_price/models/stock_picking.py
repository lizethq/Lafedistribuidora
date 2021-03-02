from odoo import models,fields,api,_

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def update_action_assign(self):
        self.action_assign()
        for record in self.move_line_ids_without_package:
            record.qty_done = record.product_uom_qty
        