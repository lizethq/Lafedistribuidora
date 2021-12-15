from odoo import models,fields,api
import logging
from itertools import chain
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class EconomicActivity(models.Model):

    _name = 'economic.activity'
    _description = 'Partner Economic Sector'

    name = fields.Char('Actividad económica')
    code = fields.Integer('CCODIGO')
