# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    delivery_report_by_category = fields.Boolean(string="Delivery Slip Report by Category")
