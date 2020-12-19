# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rack = fields.Char('Rack')
    file = fields.Char('Fila')
    case = fields.Char('Caso')