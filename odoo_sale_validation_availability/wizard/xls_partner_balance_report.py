# -*- coding: utf-8 -*-

import io
import base64

from odoo import models, fields
from datetime import date, datetime, timedelta
import xlsxwriter

import logging

_logger = logging.getLogger(__name__)

class XlsPartnerBalanceReport(models.TransientModel):

    _name = 'xls.partner.balance.report'
    _description = 'Xls Partner Balance Report'


    start_date = fields.Date(required=True, string="Fecha Inicial")
    end_date = fields.Date(required=True, string="Fecha Final")
    account_ids = fields.Many2many('account.account', string="Cuenta")
    partner_ids = fields.Many2many('res.partner', string='Tercero')
    company_id = fields.Many2one('res.company', string='Empresa')
    with_zero_balance = fields.Boolean(string='Incluir registros con balance en 0')
    xls_output = fields.Binary(
        string='Download',
        readonly=True,
    )
    
    
    def action_generate_xls(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Balance por Tercero')
        date_default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'num_format': 'yyyy-mm-dd', 'align': 'right'})
        
        merge_format = workbook.add_format({
            'bold':     True,
            'border':   0,
            'align':    'center',
            'valign':   'vcenter',
            'fg_color': '#ffe58f',
        })
        merge_subtitle_format = workbook.add_format({
            'bold':     True,
            'border':   1,
            'align':    'center',
            'valign':   'vcenter',
        })
        money = workbook.add_format({'num_format': '$#,##0'})
        money_bold = workbook.add_format({'num_format': '$#,##0','bold':True, 'fg_color': '#ffe58f'})
        bold = workbook.add_format({'bold':True, 'fg_color': '#ffe58f'})

        
        worksheet.merge_range('A2:F2', 'BALANCE CONTABLE POR TERCERO', merge_format)
        worksheet.merge_range('A3:B3', 'Fecha de Impresión: %s' % (fields.datetime.now()),merge_format)
        worksheet.merge_range('C3:D3', 'Fecha desde: %s' % (self.start_date), merge_format)
        worksheet.merge_range('E3:F3', 'Fecha hasta: %s' % (self.end_date), merge_format)

        row = 5
        
        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 30)
        worksheet.set_column(2, 2, 25)
        worksheet.set_column(3, 3, 40)
        worksheet.set_column(4, 7, 25)
        
        worksheet.write(row, 0, 'CÓDIGO', merge_subtitle_format)
        worksheet.write(row, 1, 'CUENTA', merge_subtitle_format)
        worksheet.write(row, 2, 'REFERENCIA', merge_subtitle_format)
        worksheet.write(row, 3, 'TERCERO', merge_subtitle_format)
        worksheet.write(row, 4, 'SALDO INICIAL', merge_subtitle_format)
        worksheet.write(row, 5, 'DÉBITO', merge_subtitle_format)
        worksheet.write(row, 6, 'CRÉDITO', merge_subtitle_format)
        worksheet.write(row, 7, 'SALDO FINAL', merge_subtitle_format)
        
        row += 1
        initial_value = 0
        accumulated_avg_cost = 0
        product_ctl = False
        
        domain = [('deprecated', '=', False)]
        account_ids = self.env['account.account'].search(domain)
        
        company_where = ''
        if self.company_id:
            company_where = 'and aml.company_id = %s' % (self.company_id.id)
            
        account_where = ''
        if self.account_ids:
            account_ids = ''
            count = 0
            for account in self.account_ids:
                count += 1
                account_ids += str(account.id)
                if count < len(self.account_ids):
                    account_ids += ','

            account_where = 'and aml.account_id in (%s)' % (account_ids)

        partner_where = ''
        if self.partner_ids:
            count = 0
            partner_ids = ''
            for partner in self.partner_ids:
                count += 1
                partner_ids += str(partner.id)
                if count < len(self.partner_ids):
                    partner_ids += ','
                
            partner_where = 'and aml.partner_id in (%s)' % (partner_ids)
        
        sql = """
            select 
            account.code as account_code,
            account.name as account_name,
            partner.name as partner_name,
            partner.vat as partner_document,
            partner.id as partner_id
            --sum(debit) as debit,
            --sum(credit) as credit
            
            from account_move_line aml
            left join account_move am on aml.move_id = am.id
            left join res_partner partner on aml.partner_id = partner.id
            left join account_account account on account.id = aml.account_id
            
            where 1=1
            and account.deprecated = 'f'
            and aml.date <= '%s'
            and am.state in ('posted')
            --and partner.id = 125566
            --and account.id = 6441
            %s
            %s
            %s
            
            group by
            account.code,
            account.name,
            partner.name,
            partner.vat,
            partner.id
            
            order by account.code,partner.name
                
        """ % (self.end_date, company_where, account_where, partner_where)
        self.env.cr.execute(sql)
        account_ids = self.env.cr.fetchall()
        _logger.error(sql)
        account_code_ctl = None
        account_name_ctl = None
        initial_ctl = 0
        final_ctl = 0
        debit_ctl = 0
        credit_ctl = 0
        account_count = 0
        count = 0
        
        for account in account_ids:
            
            count += 1
            if (account_code_ctl != account[0] and account_count) or len(account_ids) == count:

                worksheet.write(row, 0, account_code_ctl, money_bold)
                worksheet.write(row, 1, account_name_ctl, money_bold)
                worksheet.write(row, 2, '')
                worksheet.write(row, 3, '')
                worksheet.write(row, 4, initial_ctl, money_bold)
                worksheet.write(row, 7, final_ctl, money_bold)
                worksheet.write(row, 5, debit_ctl, money_bold)
                worksheet.write(row, 6, credit_ctl, money_bold)
                
                account_code_ctl = account[0]
                account_name_ctl = account[1]
                initial_ctl = 0
                final_ctl = 0
                debit_ctl = 0
                credit_ctl = 0
                account_count = 0
                row += 1

            #else:
                    
                
            account_code_ctl = account[0]
            worksheet.write(row, 0, account[0])
            worksheet.write(row, 1, account[1])
            worksheet.write(row, 2, account[3])
            worksheet.write(row, 3, account[2])

            if account[0]:
                if account[4]:
                    #_logger.error(account[0])
                    #_logger.error(account[4])
                    sql = """
                        select 
                        sum(aml.debit) - sum(aml.credit) as initial_balance

                        from account_move_line aml
                        left join account_move am on aml.move_id = am.id
                        left join res_partner partner on aml.partner_id = partner.id
                        left join account_account account on account.id = aml.account_id

                        where 1=1
                        and account.deprecated = 'f'
                        and aml.date < '%s'
                        and am.state in ('posted')
                        and partner.id = %s
                        and account.code = '%s'
                    """ % (self.start_date,  account[4], account[0])
                else:
                    sql = """
                        select 
                        sum(aml.debit) - sum(aml.credit) as initial_balance

                        from account_move_line aml
                        left join account_move am on aml.move_id = am.id
                        left join res_partner partner on aml.partner_id = partner.id
                        left join account_account account on account.id = aml.account_id

                        where 1=1
                        and account.deprecated = 'f'
                        and aml.date < '%s'
                        and am.state in ('posted')
                        and partner.id is null
                        and account.code = '%s'
                    """ % (self.start_date, account[0])
                self.env.cr.execute(sql)
                initial_balance = self.env.cr.fetchone()
                if initial_balance:
                    for initial in initial_balance:
                        worksheet.write(row, 4, initial if initial else 0, money)
                        initial_ctl += initial if initial else 0
            else:
                worksheet.write(row, 4, 0, money)

            if account[0]:
                if account[4]:
                    sql = """
                       select 
                        sum(aml.debit) as debit,
                        sum(aml.credit) as credit

                        from account_move_line aml
                        left join account_move am on aml.move_id = am.id
                        left join res_partner partner on aml.partner_id = partner.id
                        left join account_account account on account.id = aml.account_id

                        where 1=1
                        and account.deprecated = 'f'
                        and aml.date >= '%s'
                        and aml.date <= '%s'
                        and am.state in ('posted')
                        and partner.id = %s
                        and account.code = '%s'
                    """ % (self.start_date, self.end_date, account[4], account[0])
                    self.env.cr.execute(sql)
                    dc_balance = self.env.cr.fetchall()
                    if dc_balance:
                        for dc in dc_balance:
                            worksheet.write(row, 5, dc[0] if dc[0] else 0, money)
                            worksheet.write(row, 6, dc[1] if dc[1] else 0, money)
                            debit_ctl += dc[0] if dc[0] else 0
                            credit_ctl += dc[1] if dc[1] else 0
                        
                        
                else:
                    sql = """
                       select 
                        sum(aml.debit) as debit,
                        sum(aml.credit) as credit

                        from account_move_line aml
                        left join account_move am on aml.move_id = am.id
                        left join res_partner partner on aml.partner_id = partner.id
                        left join account_account account on account.id = aml.account_id

                        where 1=1
                        and account.deprecated = 'f'
                        and aml.date >= '%s'
                        and aml.date <= '%s'
                        and am.state in ('posted')
                        and partner.id is null
                        and account.code = '%s'
                    """ % (self.start_date, self.end_date, account[0])
                    self.env.cr.execute(sql)
                    dc_balance = self.env.cr.fetchall()
                    if dc_balance:
                        for dc in dc_balance:
                            worksheet.write(row, 5, dc[0] if dc[0] else 0, money)
                            worksheet.write(row, 6, dc[1] if dc[1] else 0, money)
                            debit_ctl += dc[0] if dc[0] else 0
                            credit_ctl += dc[1] if dc[1] else 0
                    

            else:
                worksheet.write(row, 5, 0, money)
                worksheet.write(row, 6, 0, money)


            if account[0]:
                if account[4]:
                    sql = """
                        select 
                        sum(aml.debit) - sum(aml.credit) as final_balance

                        from account_move_line aml
                        left join account_move am on aml.move_id = am.id
                        left join res_partner partner on aml.partner_id = partner.id
                        left join account_account account on account.id = aml.account_id

                        where 1=1
                        and account.deprecated = 'f'
                        and aml.date <= '%s'
                        and am.state in ('posted')
                        and partner.id = %s
                        and account.code = '%s'
                    """ % (self.end_date, account[4], account[0])
                else:
                    sql = """
                        select 
                        sum(aml.debit) - sum(aml.credit) as final_balance

                        from account_move_line aml
                        left join account_move am on aml.move_id = am.id
                        left join res_partner partner on aml.partner_id = partner.id
                        left join account_account account on account.id = aml.account_id

                        where 1=1
                        and account.deprecated = 'f'
                        and aml.date <= '%s'
                        and am.state in ('posted')
                        and partner.id is null
                        and account.code = '%s'
                    """ % (self.end_date,  account[0])
                self.env.cr.execute(sql)
                final_balance = self.env.cr.fetchone()
                if final_balance:
                    for final in final_balance:
                        worksheet.write(row, 7, final, money)
                        final_ctl += final
            else:
                worksheet.write(row, 7, 0, money)



                if not initial_ctl and not final_ctl and not account[5] and not account[6] and not self.with_zero_balance:
                    row -= 1

            row += 1
            account_count += 1

        
            
        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        self.xls_output = base64.encodestring(generated_file)

        return {
            'context': self.env.context,
            'name': 'Balance por Tercero',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'xls.partner.balance.report',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
        


class DownloadVAluation(models.Model):
    _name = 'xls.partner.balance.report.download'

    name = fields.Char(
        'File Name'
    )
    xls_output = fields.Binary(
        string='Download',
        readonly=True,
    )

