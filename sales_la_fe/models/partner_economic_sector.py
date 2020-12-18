from odoo import models,fields,api
import logging
from itertools import chain
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError



logger = logging.getLogger(__name__)


class PartnerEconomicSector(models.Model):
    
    _name = 'partner.economic.sector'
    _description = 'Partner Economic Sector'

    name = fields.Char('Sector')