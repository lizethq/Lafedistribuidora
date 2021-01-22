# -*- coding: utf-8 -*-

from odoo import models, fields, api
import pandas
from datetime import datetime
from odoo.exceptions import UserError

TYPE2REFUND = {
    'out_invoice': 'Factura de Cliente',
    'in_invoice': 'Factura de Proveedor',
    'out_refund': 'Devolucion de Cliente',
    'in_refund': 'Devolucion de Proveedor',
}


# class resPartner(models.Model):
#     _inherit = 'res.partner'
#
#     documentnumber = fields.Char(string='documentnumber')


class ReportInvoicingWizard(models.TransientModel):
    _name = 'report.invoicing.wizard'
    _description = 'Report invoicing Wizard'
    
    date_from = fields.Date(string='Date from', required=True, translate=True)
    date_to = fields.Date(string='Date to', required=True, translate=True)
    type = fields.Selection(
        [('out_invoice', 'Customer Invoice'), ('in_invoice', 'Vendor Bill'), ('out_refund', 'Customer Refund'),
         ('in_refund', 'Vendor Refund'), ('in_invoice_refund', 'Vendor Bill/Refund'),
         ('out_invoice_refund', 'Customer Invoice/Refund')],
        string='Type', default='out_invoice', translate=True)
    detailed = fields.Boolean(string='Detailed', default=True, index=True, translate=True)
    partner_ids = fields.Many2many('res.partner', string='Partner', translate=True)
    
    # @api.multi
    def generate(self):
        self.env.cr.execute(''' DELETE FROM report_invoicing ''')
        # invoicing
        self.env.cr.execute(
            ''' INSERT INTO report_invoicing(date_from, date_to, type, detailed) VALUES ('{}','{}','{}',{}) RETURNING ID'''.format(
                self.date_from, self.date_to, self.type, self.detailed))
        report_id = self.env.cr.fetchone()
        report_id = report_id[0] if report_id else False
        if not report_id:
            raise UserError(''' ''')
        # invoicing line
        type = "type = '{}'".format(self.type)
        if self.type == 'in_invoice_refund':
            type = "type in {}".format(tuple(['in_invoice', 'in_refund']))
        elif self.type == 'out_invoice_refund':
            type = "type in {}".format(tuple(['out_invoice', 'out_refund']))
        partner_ids = self.partner_ids
        if not partner_ids:
            partner_ids = self.env['res.partner'].search([])
        filter = {'report_id': report_id, 'date_from': self.date_from, 'date_to': self.date_to, 'type': type}
        filter['partner_ids'] = '(' + ','.join([str(x.id) for x in partner_ids]) + ')'
        self.env.cr.execute(''' INSERT INTO report_invoicing_line(report_id, type, invoice_id, amount_discount, partner_id, date_invoice, amount_untaxed, amount_total)
                            SELECT
                                {report_id},
                                ai.type,
                                ai.id,
                                0, --ai.amount_discount,
                                ai.partner_id,
                                ai.date_invoice,
                                ai.amount_untaxed,
                                ai.amount_total
                            FROM
                                account_invoice ai
                                WHERE
                                    ai.date_invoice BETWEEN '{date_from}'
                                    AND '{date_to}'  AND {type}
                                    AND ai.partner_id IN {partner_ids} '''.format(**filter))
        self.env.cr.commit()
        self.env.cr.execute(''' INSERT INTO report_invoicing_line_tax(line_id, name, base, amount )
                                    SELECT
                                    ril.id,
                                    at.description,
                                    (SELECT SUM(ail.price_subtotal) FROM account_invoice_line_tax ailt
                                            INNER JOIN account_invoice_line AIL ON ail.id = ailt.invoice_line_id
                                            WHERE ail.invoice_id = ait.invoice_id
                                            AND ailt.tax_id = at.id) as base,
                                    COALESCE(ait.amount,0)
                                FROM
                                    report_invoicing_line ril
                                    INNER JOIN account_invoice_tax ait ON ait.invoice_id = ril.invoice_id
                                    INNER JOIN account_tax at ON at.id = ait.tax_id ''')
        # agregar los impuestos que faltan para no descuadrar el pdf
        self.env.cr.execute(''' INSERT INTO report_invoicing_line_tax(name, line_id, base, amount )
                                    SELECT
                                        DISTINCT name, ril.id, 0,0
                                    FROM
                                        report_invoicing_line_tax ailt,
                                        report_invoicing_line ril
                                    WHERE ailt.name NOT IN (
                                        SELECT
                                            a.name
                                        FROM
                                            report_invoicing_line_tax a
                                        WHERE
                                            a.line_id = ril.id) ''')
        # self.env.cr.execute(''' select DISTINCT line_id from report_invoicing_line_tax ''')
        # taxes = self.env.cr.dictfetchall()
        header = {'report_id': report_id, 'type': self.type, 'date_from': self.date_from, 'date_to': self.date_to}
        if not self.detailed:
            self.env.cr.execute(''' INSERT INTO report_invoicing_line(report_id, amount_discount, amount_untaxed, amount_total)
                                        SELECT {}, SUM(amount_discount), SUM(amount_untaxed), SUM(amount_total) FROM report_invoicing_line RETURNING ID'''.format(
                report_id))
            id = self.env.cr.fetchone()
            if id:
                id = id[0]
                self.env.cr.execute(''' UPDATE report_invoicing_line_tax SET line_id = {} '''.format(id))
                self.env.cr.execute(''' DELETE FROM report_invoicing_line WHERE partner_id IS NOT NULL  ''')
        
        self.env.cr.execute(
            ''' select distinct name from report_invoicing_line_tax where name is not null ORDER BY name ''')
        taxes = self.env.cr.dictfetchall()
        cases = ""
        for tax in taxes:
            cases += " COALESCE((SELECT SUM(base) FROM report_invoicing_line_tax WHERE line_id = ril.id AND name = '{tax}'),0) as BASE_{tax}, " \
                     " COALESCE((SELECT SUM(amount) FROM report_invoicing_line_tax WHERE line_id = ril.id AND name = '{tax}'),0) as {tax}, ".format(
                tax=tax.get('name', 'undefined'))
        self.env.cr.execute(
            ''' SELECT
                    COALESCE(ai.number, ai.name) AS "Factura",
                    ril.date_invoice AS "Fecha de factura",
                    COALESCE(rp.documentnumber) AS "NIT",
                    COALESCE(rp.name) AS "Tercero",
                    {}
                    ai.amount_discount AS "Descuento",
                    ril.amount_untaxed AS "Subtotal",
                    ril.amount_total AS "Total"
                FROM
                    report_invoicing_line ril
                    LEFT JOIN account_invoice ai ON ai.id = ril.invoice_id
                    LEFT JOIN res_partner rp ON rp.id = ai.partner_id
                    WHERE ril.report_id = {}
                GROUP BY
                    ril.id,
                    ai.number,
                    ai.name,
                    ril.date_invoice,
                    rp.documentnumber,
                    rp.name,
                    ai.amount_discount,
                    ril.amount_untaxed,
                    ril.amount_total
                ORDER BY ai.number, ai.name '''.format(cases, report_id))
        return {'columns': [x[0] if x else 'undefined' for x in self.env.cr.description], 'header': header,
                'lines': self.env.cr.dictfetchall()}
    
    # @api.multi
    def generate_excel(self):
        data = self.generate()
        if data:
            columns = data.get('columns')
            header = data.get('header')
            data = data.get('lines')
            model = 'report.invoicing'
            name = model.replace('.', '_')
            format = '.xlsx'
            report = self.env[model].browse(header.get('report_id'))
            data_attach = {
                'name': name + '-' + format,
                'datas': '.',
                'datas_fname': name + '-' + format,
                'res_model': model,
                'res_id': report.id,
            }
            self.env['ir.attachment'].search(
                [('res_model', '=', model), ('company_id', '=', self.env.user.company_id.id),
                 ('name', 'like', '%' + name + '%' + self.env.user.name + '%')]).unlink()
            attachments = self.env['ir.attachment'].create(data_attach)
            url = self.env['ir.config_parameter'].get_param('web.base.url') + '/web/content/%s?download=true' % str(
                attachments.id)
            path = attachments.store_fname
            df = pandas.DataFrame.from_dict(data)
            
            writer = pandas.ExcelWriter(attachments._full_path(path), engine='xlsxwriter')
            
            df = df.append(df.sum(numeric_only=True), ignore_index=True)
            
            new_column = pandas.Series([''], name='Factura', index=[max(df.index.tolist())])
            df.update(new_column)
            new_column = pandas.Series([''], name='Fecha de factura', index=[max(df.index.tolist())])
            df.update(new_column)
            new_column = pandas.Series([''], name='NIT', index=[max(df.index.tolist())])
            df.update(new_column)
            new_column = pandas.Series(['TOTALES'], name='Tercero', index=[max(df.index.tolist())])
            df.update(new_column)
            
            df.reindex(columns=columns).to_excel(writer,
                                                 sheet_name=name,
                                                 startrow=6, index=False)
            worksheet = writer.sheets[name]
            worksheet.write(0, 0, self.env.user.company_id.partner_id.display_name)
            worksheet.write(1, 0, 'FECHA DE GENERACION: ' + str(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
            worksheet.write(3, 0, 'TIPO: ' + TYPE2REFUND.get(self.type))
            worksheet.write(4, 0, name)
            worksheet.write(5, 0, 'PERIODO REAL CONSULTADO: ' + self.date_from + '-' + self.date_to)
            writer.save()
            return {'type': 'ir.actions.act_url', 'url': str(url), 'target': 'new'}
    
    # @api.multi
    def generate_pdf(self):
        data = self.generate()
        header = data.get('header', {})
        report = self.env['report.invoicing'].browse(header.get('report_id'))
        return report.env['report'].get_action(report, 'reports.report_invoicing_format')


class ReportInvoicing(models.Model):
    _name = 'report.invoicing'
    _description = 'Report invoicing'
    
    date_from = fields.Date(string='Date from', required=True, translate=True)
    date_to = fields.Date(string='Date to', required=True, translate=True)
    type = fields.Selection(
        [('out_invoice', 'Customer Invoice'), ('in_invoice', 'Vendor Bill'), ('out_refund', 'Customer Refund'),
         ('in_refund', 'Vendor Refund'), ('in_invoice_refund', 'Vendor Bill/Refund'),
         ('out_invoice_refund', 'Customer Invoice/Refund')],
        string='Type', default='out_invoice', translate=True)
    detailed = fields.Boolean(string='Detailed', default=False, index=True, translate=True)
    line_ids = fields.One2many('report.invoicing.line', 'report_id', string='Lines', translate=True)


class ReportInvoicingLine(models.Model):
    _name = 'report.invoicing.line'
    _description = 'Report invoicing line'
    
    report_id = fields.Many2one('report.invoicing', string='Report', required=True, index=True, ondelete='cascade')
    invoice_id = fields.Many2one('account.invoice', string='Invoice', index=True, ondelete='cascade', translate=True)
    type = fields.Selection(
        [('out_invoice', 'Customer Invoice'), ('in_invoice', 'Vendor Bill'), ('out_refund', 'Customer Refund'),
         ('in_refund', 'Vendor Refund'), ('in_invoice_refund', 'Vendor Bill/Refund'),
         ('out_invoice_refund', 'Customer Invoice/Refund')],
        string='Type', default='out_invoice', translate=True)
    amount_discount = fields.Float(string='Discount', default=0, translate=True)
    date_invoice = fields.Date(string='Date invoice', translate=True)
    partner_id = fields.Many2one('res.partner', string='Partner', index=True, ondelete='cascade', translate=True)
    tax_ids = fields.One2many('report.invoicing.line.tax', 'line_id', string='Tax line', translate=True)
    amount_untaxed = fields.Float(string='Subtotal', default=0, translate=True)
    amount_total = fields.Float(string='Total', default=0, translate=True)


class ReportInvoicingLineTax(models.Model):
    _name = 'report.invoicing.line.tax'
    _description = 'Report invoicing line tax'
    
    line_id = fields.Many2one('report.invoicing.line', string='Line', required=True, index=True, ondelete='cascade',
                              translate=True)
    name = fields.Char(string='Name', default=0, translate=True)
    base = fields.Float(string='Base', default=0, translate=True)
    amount = fields.Float(string='Amount', default=0, translate=True)
