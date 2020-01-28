# -*- coding: utf-8 -*-
{
    'name': "alloy quality control slip",
    'summary': """
        alloy quality control slip""",
    'description': """
        alloy quality control slip
    """,
    'author': "Magdy, Telenoc",
    'website': "http://www.yourcompany.com",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base', 'sale','crm_source', 'web_digital_sign'],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_report.xml',
        'report/sales_report.xml',
    ],
}