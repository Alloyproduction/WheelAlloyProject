# -*- coding: utf-8 -*-
{
    'name': "Alloy purchase order approval",
    'summary': """Alloy purchase order approval""",
    'description': """Alloy purchase order approval""",
    'author': "Magdy, helcon",
    'website': "http://www.yourcompany.com",
    'category': 'purchase',
    'version': '0.1',
    'depends': ['base','mail', 'purchase'],
    'data': [
         # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/purchase_view.xml',
       # 'views/mail_template.xml',
    ],
}
