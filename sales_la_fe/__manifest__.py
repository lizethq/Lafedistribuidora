# -*- coding: utf-8 -*-
{
    'name': "sales_la_fe",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'sale', 'dev_customer_credit_limit','product_expiry'],
    #
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner_economic_sector_view.xml',
        'views/res_partner_economic_sector_view.xml',
        'views/account_move_la_fe_expiration_date_view.xml',
        'views/product_pivote_view.xml',
        'views/product_template_sales_la_fe.xml',
        'views/sale_order_sales_la_fe_view.xml',
        'views/stock_production_lot_la_fe.xml'
        #'views/sale_order_chanel_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}