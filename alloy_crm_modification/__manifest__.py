# -*- coding: utf-8 -*-
{
    'name': "Alloy Crm Modification",
    'summary': """Alloy Crm Modification""",
    'description': """Alloy Crm Modification""",
    'author': "Magdy, helcon",
    'website': "http://www.yourcompany.com",
    'category': 'crm',
    'version': '0.1',
    'depends': ['base', 'sale_crm', 'sale', 'portal'],
    # 'qweb': [
    #     "static/src/xml/portal_signature.xml",
    # ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/crm_view.xml',
    ],
}
