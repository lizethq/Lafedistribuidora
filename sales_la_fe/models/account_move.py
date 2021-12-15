# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied


class AccountMove(models.Model):
    _inherit = 'account.move'

    new_expiration_date = fields.Date('Fecha de Vencimiento')
