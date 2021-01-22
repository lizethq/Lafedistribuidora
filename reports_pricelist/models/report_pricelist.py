# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportPricelist(models.Model):
    _name = 'report.pricelist'
    _description = 'Report pricelist'
    
    in_stock = fields.Boolean(string='In stock', default=False, index=True, translate=True)
    line_ids = fields.One2many('report.pricelist.line', 'report_id', string='Lines', translate=True)
    # pdf_ids = fields.One2many('report.pricelist.pdf.line', 'report_id', string='PDF', translate=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', translate=True)