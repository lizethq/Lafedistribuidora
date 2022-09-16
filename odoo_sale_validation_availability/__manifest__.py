# -*- coding: utf-8 -*-
{
    'name': "odoo_sale_validation_availability",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'sale',
        'sale_stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/product_available_log.xml',
        'wizard/xls_partner_balance_report.xml',
    ],
    'installable': True,
    'application': True,
}

