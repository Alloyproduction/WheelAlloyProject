# -*- coding: utf-8 -*-
{
    'name': "Alloywheel Modification",
    'summary': """
        Alloywheel Modification""",
    'description': """
        Alloywheel Modification
    """,
    'author': "Magdy, helcon",
    'website': "http://www.yourcompany.com",
    'category': 'inventory',
    'version': '0.1',
    'depends': ['base','stock', 'sale', 'project','account', 'product', 'sale_enterprise'],
    'data': [
        'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/sale_report.xml',
    ],
}
