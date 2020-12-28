# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sector_id = fields.Many2one('partner.economic.sector','Sector')
    #economic_activity_id = fields.Many2one('economic.activity', 'Actividad económica')
    gender = fields.Selection([('Masculino', 'Masculino'), ('Femenino', 'Femenino'), ('Indeterminado', 'Indeterminado')], 'Genero')
    study_credit = fields.Selection([('Si', 'Si'), ('No', 'No')], 'Estudio de credito aprobado?')
    ciiu_ids = fields.Many2many('ciiu.code', 'partner_ciiu_rel','partner_id', 'ciiu_id', string='Actividad económica' )
    #economic_activity_ids = fields.Many2many('ciiu.code', 'partner_acteco_rel','partner_id', 'ciiu_code_id', string='Actividad económica' )
    
    
    