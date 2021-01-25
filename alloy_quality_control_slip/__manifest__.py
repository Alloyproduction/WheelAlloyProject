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
    'depends': ['base', 'sale', 'web_digital_sign'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/sales_report.xml',
        'views/mail_notification.xml',
        'views/email_templete.xml',
        'report/sales_report.xml',
    ],
}
