# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sector_id = fields.Many2one('partner.economic.sector','Sector')
    