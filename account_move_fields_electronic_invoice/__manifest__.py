# -*- coding: utf-8 -*-
{
    'name': "account_move_fields_electronic_invoice",

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
    'depends': ['account', 'sale_stock','sales_la_fe', 'jt_amount_in_words'],
    #
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/partner_economic_sector_view.xml',
        #'views/res_partner_economic_sector_view.xml',
        #'views/account_move_la_fe_expiration_date_view.xml'
        'views/res_partner_economic_sector_view.xml',
        #'viwes/account_move_invoice_electronic_lafe.xml',
        'reports/account_invoice_la_fe.xml',
        'reports/container_factura_electronica_la_fe.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}