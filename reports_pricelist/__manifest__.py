# -*- coding: utf-8 -*-
{
    'name': "Reports Pricelist",
    
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    
    'description': """
        Long description of module's purpose
    """,
    
    'author': "Todoo SAS",
    'website': "http://www.todoo.co",
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',
    
    # any module necessary for this one to work correctly
    'depends': ['account_accountant', 'sale', 'sales_team', 'purchase'],
    
    # always loaded
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        # 'views/invoicing.xml',
        # 'views/invoicing_template.xml',
        'views/pricelist.xml',
        'views/pricelist_template.xml',
        # 'views/sale_invoice.xml',
        # 'views/sale_invoice_template.xml',
    ],
}
