# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    person_type = fields.Selection([("1", "Juridical Person and assimilated"),
                                    ("2", "Natural Person and assimilated")], string="Person Type")