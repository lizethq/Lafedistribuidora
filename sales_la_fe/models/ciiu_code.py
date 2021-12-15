from odoo import models,fields,api
import logging
from itertools import chain
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class PartnerEconomicSector(models.Model):

    _name = 'ciiu.code'
    _description = 'Ciiu Code '

    name = fields.Char('Codigo')
    description = fields.Char('Descripción')
