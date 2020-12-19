from odoo import models,fields,api
import logging
from itertools import chain
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError



logger = logging.getLogger(__name__)


class PaymentMethodsLaFe(models.Model):
    
    _name = 'payment.methods.la.fe'
    _description = 'Payment Methods La Fe '

    name = fields.Char('Medio de pago')
    