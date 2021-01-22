# -*- coding: utf-8 -*-
import pandas
from pytz import timezone
from datetime import datetime
from base64 import b64encode, b64decode

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ReportPricelistWizard(models.TransientModel):
    _name = 'report.pricelist.wizard'
    _description = 'Report pricelist Wizard'
    
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', translate=True, required=True)
    category_ids = fields.Many2many('product.category', string='Category', translate=True)
    in_stock = fields.Boolean(string='In stock', default=False, index=True, translate=True)
    
    # @api.multi
    def generate(self):
        self.env.cr.execute(''' DELETE FROM report_pricelist ''')
        # pricelist
        self.env.cr.execute(
            ''' INSERT INTO report_pricelist(in_stock, pricelist_id) 
                    VALUES ({stock},{pricelist}) RETURNING ID'''.format(stock=self.in_stock, 
                                                                        pricelist=self.pricelist_id.id))
        report_id = self.env.cr.fetchone()
        report_id = report_id[0] if report_id else False
        if not report_id:
            raise UserError(''' ''')
        
        pricelist_id = self.pricelist_id
        if not pricelist_id:
            pricelist_id = self.env['product.pricelist'].search([])
        pricelist = " AND ppi.pricelist_id = {}".format(pricelist_id.id)
              # .format('(' + ','.join([str(x.id) for x in pricelist_ids]) + ')')
        
        category_ids = self.category_ids
        if not category_ids:
            category_ids = self.env['product.category'].search([])
        
        filter = {'report_id': report_id}  # 'in_stock': self.in_stock
        
        filter['pricelist'] = pricelist
        filter['category_ids'] = '(' + ','.join([str(x.id) for x in category_ids]) + ')'
        filter['stock'] = ''
        if self.in_stock:
            filter['stock'] = " WHERE a.qty > 0 "
        
        self.env.cr.execute(''' INSERT INTO report_pricelist_line(report_id, pricelist_item_id, product_id, qty)
                                        SELECT {report_id} as report_id, * 
                                        FROM (SELECT ppi.id, pp.id, (SELECT COALESCE(SUM(sq.quantity), 0)
                                                                    FROM stock_quant sq
                                                                    INNER JOIN stock_location sl ON sl.id = sq.location_id
                                                                    WHERE sq.product_id = pp.id
                                                                    AND sl.usage = 'internal'
                                                                    AND active IS TRUE) AS qty
                                              FROM product_product pp
                                              INNER JOIN product_template pt ON pt.id = pp.product_tmpl_id
                                              INNER JOIN product_category pc ON pc.id = pt.categ_id
                                              LEFT JOIN product_pricelist_item ppi ON (ppi.product_tmpl_id = pt.id OR ppi.product_id = pp.id OR ppi.applied_on = '3_global')
                                              WHERE pt.active IS TRUE
                                              AND pt.sale_ok IS TRUE
                                              {pricelist}
                                              AND (pt.categ_id IN {category_ids} OR pt.categ_id is NULL)
                                              ORDER BY pt.name) AS a 
                                        {stock} '''.format(**filter))
        
        header = {'report_id': report_id, 'in_stock': self.in_stock}
        self.env.cr.commit()
        # insert = ''
        if not self.env.context.get('pdf', False):
            #     insert = ''' INSERT INTO report_pricelist_pdf_line(default_code, name, qty, amountwithouttax, amountwithtax) '''
            self.env.cr.execute(''' SELECT pt.default_code AS "CODIGO DEL PRODUCTO",
                                           pt.name AS "DESCRIPCION DEL PRODUCTO",
                                           qty AS "CANTIDAD A LA MANO",
                                           round(COALESCE(  (CASE WHEN ppi.fixed_price > 0 
                                                                  THEN ppi.fixed_price
                                                                  ELSE NULL
                                                                  END), 
                                                            (CASE WHEN ppi.percent_price > 0 
                                                                  THEN ppi.percent_price / 100 * pt.list_price
                                                                  ELSE NULL
                                                                  END)::numeric, 
                                                            (CASE WHEN ppi.compute_price = 'formula' 
                                                                  THEN pt.list_price - pt.list_price * ppi.price_discount / 100
                                                                  ELSE NULL
                                                                  END)::numeric,
                                                            pt.list_price) 
                                                + ppi.price_surcharge, 2) AS "VALOR SIN IMPUESTO", 
                                           (round((at.amount / 100), 2) * 100)::character varying || '%' AS "IMPUESTO",
                                           round(COALESCE((at.amount / 100), 0) * (COALESCE((CASE WHEN ppi.fixed_price > 0 
                                                                                                   THEN ppi.fixed_price
                                                                                                   ELSE NULL
                                                                                                   END), 
                                                                                            (CASE WHEN ppi.percent_price > 0 
                                                                                                  THEN ppi.percent_price / 100 * pt.list_price
                                                                                                  ELSE NULL 
                                                                                                  END)::numeric, 
                                                                                            (CASE WHEN ppi.compute_price = 'formula' 
                                                                                                  THEN pt.list_price - pt.list_price * ppi.price_discount / 100
                                                                                                  ELSE NULL
                                                                                                  END)::numeric,
                                                                                            pt.list_price)
                                                                                    + ppi.price_surcharge)
                                                            + (COALESCE(( CASE WHEN ppi.fixed_price > 0 
                                                                                THEN ppi.fixed_price 
                                                                                ELSE NULL
                                                                                END), 
                                                                        ( CASE WHEN ppi.percent_price > 0 
                                                                                THEN ppi.percent_price / 100 * pt.list_price
                                                                                ELSE NULL
                                                                                END)::numeric, 
                                                                        ( CASE WHEN ppi.compute_price = 'formula' 
                                                                                THEN pt.list_price - pt.list_price * ppi.price_discount / 100
                                                                                ELSE NULL 
                                                                                END)::numeric,
                                                                        pt.list_price) + ppi.price_surcharge), 2) AS "VALOR CON IMPUESTO"
                                    FROM report_pricelist_line rpl
                                    LEFT JOIN product_product pp ON pp.id = rpl.product_id
                                    LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                                    LEFT JOIN product_pricelist_item ppi ON ppi.id = rpl.pricelist_item_id
                                    LEFT JOIN product_pricelist ppl ON ppl.id = ppi.pricelist_id
                                    LEFT JOIN product_taxes_rel ptr ON ptr.prod_id = pp.id
                                    LEFT JOIN account_tax at ON at.id = ptr.tax_id AND at.name LIKE '%IVA%' 
                                    ORDER BY pt.name''')
            return {'columns': [x[0] if x else 'undefined' for x in self.env.cr.description], 'header': header,
                    'lines': self.env.cr.dictfetchall()}
        else:
            return report_id
        return True
    
    # @api.multi
    def generate_excel(self):
        data = self.generate()
        if data:
            columns = data.get('columns')
            header = data.get('header')
            data = data.get('lines')
            model = 'report.pricelist'
            name = 'REPORTE LISTA DE PRECIOS'
            format = '.xlsx'
            report = self.env[model].browse(header.get('report_id'))
            data_attach = {
                'name': name + '-' + format,
                'datas': '.',
                # 'datas_fname': name + '-' + format,
                'res_model': model,
                'res_id': report.id,
            }
            self.env['ir.attachment'].search([('res_model', '=', model), 
                                              ('company_id', '=', self.env.user.company_id.id),
                                              ('name', 'like', '%' + name + '%' + self.env.user.name + '%')]).unlink()
            attachments = self.env['ir.attachment'].create(data_attach)
            url = self.env['ir.config_parameter'].get_param('web.base.url') + '/web/content/%s?download=true' % str(
                attachments.id)
            path = attachments.store_fname
            df = pandas.DataFrame.from_dict(data)
            
            writer = pandas.ExcelWriter(attachments._full_path(path), engine='xlsxwriter')
            df.reindex(columns=columns).to_excel(writer,
                                                 sheet_name=name,
                                                 startrow=6, index=False)
            worksheet = writer.sheets[name]
            worksheet.write(0, 0, self.env.user.company_id.partner_id.display_name)
            worksheet.write(1, 0, 'FECHA DE GENERACION: ' + str(datetime.now().astimezone(timezone(self.env.user.tz)).strftime('%d/%m/%Y %H:%M:%S')))
            worksheet.write(3, 0, name)
            writer.save()
            return {'type': 'ir.actions.act_url', 'url': str(url), 'target': 'new'}
    
    # @api.multi
    def generate_pdf(self):
        report = self.with_context(pdf=True).generate()
        report = self.env['report.pricelist'].browse(report)
        # header = data.get('header', {})
        # report = self.env['report.pricelist'].browse(header.get('report_id'))
        # return self.env['report'].get_action(report, 'reports_pricelist.report_pricelist_format')
        # data = self.env['ir.actions.report'].report_action(report, 'reports_pricelist.report_pricelist_format')
        model = 'report.pricelist'
        name = 'REPORTE LISTA DE PRECIOS'
        format = '.pdf'
        pdf = self.env.ref('reports_pricelist.report_pricelist_format_action').render_qweb_pdf(report.id)
        pdf = b64encode(pdf[0])
        data_attach = {
                'name': name + '-' + format,
                'datas': pdf,
                # 'datas_fname': name + '-' + format,
                'res_model': model,
                'res_id': report.id,
            }
        self.env['ir.attachment'].search([('res_model', '=', model), 
                                          ('company_id', '=', self.env.user.company_id.id),
                                          ('name', 'like', '%' + name + '%' + self.env.user.name + '%')]).unlink()
        attachments = self.env['ir.attachment'].create(data_attach)
        url = self.env['ir.config_parameter'].get_param('web.base.url') + \
                    '/web/content/%s?download=true' % str(attachments.id)
        return {'type': 'ir.actions.act_url', 
                'url': str(url), 
                'target': 'new'}



# class ReportPricelistPDFLine(models.Model):
#     _name = 'report.pricelist.pdf.line'
#     _description = 'Report pricelist PDF line'
#
#     report_id = fields.Many2one('report.pricelist', string='Report', index=True, ondelete='cascade', translate=True)
#     default_code = fields.Char(string='Default code')
#     name = fields.Char(string='Name')
#     qty = fields.Float(string='Quantity', default=0)
#     amountwithouttax = fields.Float(string='Valor sin impuesto', default=0)
#     amountwithtax = fields.Float(string='Valor con impuesto', default=0)
