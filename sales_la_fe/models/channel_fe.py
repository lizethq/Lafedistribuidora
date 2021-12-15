from odoo import models,fields,api
import logging
from itertools import chain
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ChannelFe(models.Model):

    _name = 'channel.fe'
    _description = 'Channel Fe'

    name = fields.Char('Canal')
