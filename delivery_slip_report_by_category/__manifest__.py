# -*- coding: utf-8 -*-
{
    'name': 'Delivery Slip Report By Product Category',
    'summary': "Print Delivery Slip Report By Product Category",
    'description': "Print Delivery Slip Report By Product Category",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Warehouse',
    'version': '13.0.0.1.0',
    'depends': ['stock'],

    'data': [
        'views/delivery_slip_report.xml',
        'views/res_config_settings_views.xml',
    ],

    'license': "OPL-1",
    'price': 9,
    'currency': "EUR",

    'auto_install': False,
    'installable': True,

    'images': ['static/description/banner.png'],
}
