from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_cum = fields.Char('Código CUM')
    x_invima = fields.Char('Código Invima')
    x_atc = fields.Char('Código ATC')
