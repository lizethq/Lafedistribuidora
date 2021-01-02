# -*- coding: utf-8 -*-
{
    'name': "account_fiscal_extended",

    'summary': """
        Posiciones fiscales """,

    'description': """
        Posiciones fiscales 
    """,

    'author': "Todoo SAS",
    'contributors': ['Carlos Guio fg@todoo.co'],
    'website': "http://www.todoo.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': ['l10n_co_dian_data'],

    # always loaded
    'data': [
        'views/res_partner.xml',
        'views/fiscal_position.xml',
    ],
}
