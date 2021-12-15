# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessDenied


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sector_id = fields.Many2one('partner.economic.sector','Sector')
    gender = fields.Selection([('Masculino', 'Masculino'), ('Femenino', 'Femenino'), ('Indeterminado', 'Indeterminado')], 'Genero')
    study_credit = fields.Selection([('Si', 'Si'), ('No', 'No')], 'Estudio de credito aprobado?')
    ciiu_ids = fields.Many2many('ciiu.code', 'partner_ciiu_rel','partner_id', 'ciiu_id', string='Actividad económica' )
    confidence_degree = fields.Selection(
        string="Confidence degree",
        selection=[
                ('good', 'good debtor'),
                ('low', 'normal debtor'),
                ('bad', ' bad debtor'),
        ],
    )
    establishment_comercial = fields.Selection(
        selection=[
                ('si', 'Si'),
                ('no', 'No'),
        ], default=False, string='¿Establecimiento comercial?'
    )

    val_establishment = fields.Boolean('Hello', default=False)
    establishment_comercial_one = fields.Char('Establecimiento #1')
    establishment_comercial_two = fields.Char('Establecimiento #2')
    establishment_comercial_three = fields.Char('Establecimiento #3')

    #@api.onchange('establishment_comercial')
    @api.onchange('x_establecimiento')
    def _compute_val_establishment(self):
        for record in self:
            if record.x_establecimiento == 'Si':
                record.val_establishment = True
            else:
                record.val_establishment = False
