# -*- coding: utf-8 -*-
{
    'name': "POS Report Details",

    'summary': """Point of sale Report
   """,

    'description': """
       POS Report details
    """,

    'author': "Diego Carvajal",
    'website': "dracosoft.com.co",
    'category': 'Point of sale',
    'version': '0.2',
    'license': "AGPL-3",

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        'views/report_session_details.xml',
    ],
    'images': ['static/description/icon.png'],

    'installable': True,
}

