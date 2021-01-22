# -*- coding: utf-8 -*-

from odoo import models, fields, api
import pandas
from datetime import datetime
from odoo.exceptions import UserError


class ReportSaleInvoiceWizard(models.TransientModel):
    _name = 'report.sale.invoice.wizard'
    _description = 'Report Sale Invoice Wizard'
    
    date_from = fields.Date(string='Date from', required=True, translate=True)
    date_to = fields.Date(string='Date to', required=True, translate=True)
    
    # @api.multi
    def generate(self):
        self.env.cr.execute(''' DELETE FROM report_sale_invoice ''')
        # sale.invoice
        self.env.cr.execute(
            ''' INSERT INTO report_sale_invoice(date_from, date_to) VALUES ('{}','{}') RETURNING ID'''.format(
                self.date_from, self.date_to))
        report_id = self.env.cr.fetchone()
        report_id = report_id[0] if report_id else False
        if not report_id:
            raise UserError(''' ''')
        
        date_filter = 'NULL,'
        group_filter = 'rp.id'
        join = ''
        if self.env.context.get('pivot', False):
            date_filter = ' ai.date_invoice, '
            group_filter += ',ai.date_invoice, ai.id'
            join = ' INNER JOIN account_invoice_payment_rel aipr ON aipr.invoice_id = ai.id AND aipr.payment_id = ap.id '
        
        filter = {'report_id': report_id, 'date_from': self.date_from,
                  'date_to': self.date_to, 'date_filter': date_filter, 'group_filter': group_filter,'join':join}
        
        self.env.cr.execute(''' INSERT INTO report_sale_invoice_line(report_id, partner_id, period, amount_invoiced, amount_collect)
                                SELECT
                                    {report_id},
                                    rp.id,
                                    {date_filter}
                                    SUM(( CASE WHEN ai.type = 'out_invoice' THEN
                                                    COALESCE(ai.amount_total, 0)
                                                    WHEN ai.type = 'out_refund' THEN
                                                    COALESCE(ai.amount_total, 0) * - 1
                                    END)) AS amount_invoiced,
                                    (
                                        SELECT
                                            SUM(ap.amount)
                                        FROM
                                            account_payment ap
                                            {join}
                                        WHERE
                                            ap.partner_id = rp.id
                                            AND ap.payment_date BETWEEN '{date_from}'
                                            AND '{date_to}') AS amount_collect
                                FROM
                                    account_invoice ai
                                    INNER JOIN res_partner rp ON rp.id = ai.partner_id
                                    WHERE
                                        ai.type IN ('out_invoice', 'out_refund')
                                        AND ai.date_invoice BETWEEN '{date_from}' AND '{date_to}'
                                    GROUP BY
                                        {group_filter}
                                    ORDER BY rp.name '''.format(**filter))
        
        header = {'report_id': report_id, 'date_from': self.date_from, 'date_to': self.date_to}
        self.env.cr.commit()
        self.env.cr.execute(''' SELECT
                                    COALESCE(rp.documentnumber) as "NIT",
                                    rp.name as "Tercero",
                                    COALESCE(amount_invoiced,0) as "Facturado",
                                    COALESCE(amount_collect,0)as "Recaudado"
                                FROM
                                    report_sale_invoice_line rsil
                                    INNER JOIN res_partner rp ON rp.id = rsil.partner_id
                                    ORDER BY rp.name''')
        return {'columns': [x[0] if x else 'undefined' for x in self.env.cr.description], 'header': header,
                'lines': self.env.cr.dictfetchall()}
    
    # @api.multi
    def generate_excel(self):
        data = self.generate()
        if data:
            columns = data.get('columns')
            header = data.get('header')
            data = data.get('lines')
            model = 'report.sale.invoice'
            name = model.replace('.', ' ')
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
            new_column = pandas.Series([''], name='NIT', index=[max(df.index.tolist())])
            df.update(new_column)
            new_column = pandas.Series(['TOTALES'], name='Tercero', index=[max(df.index.tolist())])
            df.update(new_column)
            # new_column = pandas.Series(['TOTALES'], name='Periodo', index=[max(df.index.tolist())])
            # df.update(new_column)
            df.reindex(columns=columns).to_excel(writer,
                                                 sheet_name=name,
                                                 startrow=6, index=False)
            worksheet = writer.sheets[name]
            worksheet.write(0, 0, self.env.user.company_id.partner_id.display_name)
            worksheet.write(1, 0, 'FECHA DE GENERACION: ' + str(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
            worksheet.write(3, 0, 'REPORTE DE VENTA Y RECAUDO')
            worksheet.write(5, 0, 'PERIODO REAL CONSULTADO: ' + self.date_from + '-' + self.date_to)
            
            writer.save()
            return {'type': 'ir.actions.act_url', 'url': str(url), 'target': 'new'}
        return data
    
    # @api.multi
    def generate_pdf(self):
        data = self.generate()
        header = data.get('header', {})
        report = self.env['report.sale.invoice'].browse(header.get('report_id'))
        return report.env['report'].get_action(report, 'reports.report_sale_invoice_format')
    
    # @api.multi
    def generate_pivot(self):
        data = self.with_context({'pivot': True}).generate()
        [action] = self.env.ref('reports.report_sale_invoice_pivot_action').read()
        return action


class ReportSaleInvoice(models.Model):
    _name = 'report.sale.invoice'
    _description = 'Report sale invoice'
    
    date_from = fields.Date(string='Date from', required=True, translate=True)
    date_to = fields.Date(string='Date to', required=True, translate=True)
    line_ids = fields.One2many('report.sale.invoice.line', 'report_id', string='Lines', translate=True)


class ReportSaleInvoiceLine(models.Model):
    _name = 'report.sale.invoice.line'
    _description = 'Report sale invoice line'
    
    report_id = fields.Many2one('report.sale.invoice', string='Report', required=True, index=True, ondelete='cascade',
                                translate=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, index=True, translate=True)
    period = fields.Date(string='Period', required=False, translate=True)
    amount_invoiced = fields.Float(string='Amount invoice', default=0, translate=True)
    amount_collect = fields.Float(string='Amount collect', default=0, translate=True)
