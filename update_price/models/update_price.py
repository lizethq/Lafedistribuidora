from odoo import models,fields,api

class UpdatePrice(models.Model):
    _name = 'update.price'
    _description = 'update price'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product','Product')
    price = fields.Float('Price')

    @api.onchange('product_id')
    def _onchange_price(self):
        if self.product_id:
            self.price = self.product_id.list_price
        else:
            self.price = 0

    def action_update_price(self):
        product_obj = self.env['product.product'].search([('id','=',self.product_id.id)],limit=1)
        product_obj.write({'list_price': self.price})

            