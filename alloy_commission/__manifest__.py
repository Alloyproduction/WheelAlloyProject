# -*- coding: utf-8 -*-
{
    'name': 'Alloy Commission',
    'version': '12.0.1',
    'summary': 'Alloy Commission',
    'category': 'account',
    'author': 'Magdy Salah',
    'description': """
    Alloy Commission
    """,
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'views/account_commission.xml',
        'views/account_invoice.xml',
        'views/partner.xml',
        'views/res_config_setting.xml',
        'wizard/wiz_commission_report_view.xml',
        'report/commission_report.xml',
        'report/report_commission_account.xml',
    ]
}
