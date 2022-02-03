# -*- coding: utf-8 -*-
{
    'name': "Alloy Crm Modification",
    'summary': """Alloy Crm Modification""",
    'description': """Alloy Crm Modification""",
    'author': "Magdy, helcon ",
    'website': "http://www.yourcompany.com",
    'category': 'crm',
    'version': '0.1',
    'depends': ['base','mail', 'sale_crm', 'sale', 'portal'],
    # 'qweb': [
    #     "static/src/xml/portal_signature.xml",
    # ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sales_stages.xml',
        'views/data_stages.xml',
        'views/crm_view.xml',
        'views/wizard.xml',
        'report/crm_report_pdf.xml',
        'report/crm_report_xlx.xml',
        'report/report_crm_wizard.xml',
    ],
}
