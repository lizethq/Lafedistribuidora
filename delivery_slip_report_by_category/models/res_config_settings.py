# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    delivery_report_by_category = fields.Boolean(related='company_id.delivery_report_by_category', string="Delivery Slip Report by Category", readonly=False)
