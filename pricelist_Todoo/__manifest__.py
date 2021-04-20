# -*- coding: utf-8 -*-
#####################################################################################
#
#
#
#
#
#
#
#####################################################################################

{
    'name': "pricelist Todoo SAS",

    'summary': "pricelist",

    'description': "pricelist",

    'author': "Todoo SAS",

    'contributors': ['Luis Felipe Paternina lp@todoo.co'],

    'website': "http://www.todoo.co",

    'category': 'Tools',

    'version': '13.1',

        'depends': ['stock'],
    
    'data': [     
        
         'views/product_template.xml',
         'security/ir.model.access.csv',       
              
    ],
    
    'demo': [
        'demo/demo.xml',
    ],
}
