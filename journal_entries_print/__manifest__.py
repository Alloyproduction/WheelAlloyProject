

{
    'name': 'Journal Entries Print',
    'version': '12.0',
    'category': 'account',
    'sequence': 9,
    'summary': 'Journal Entries Print',
    'description': """
    this module use for print journal Entries in PDF report"
    """,
    'author': "Hunain Ahmed",
    'website': "http://telenoc.org",
    'depends': ['account','mail'],
    'license': 'AGPL-3',
    'data': [
            'security/groups.xml',
            'security/ir.model.access.csv',
            'report/report_menu.xml',
            'report/report_menu2.xml',
            'report/profial.xml',
            'report/claim_report.xml',
            'views/views.xml',
            ],


    "images": [
        'static/description/telenoc.jpeg'
    ],
    'demo': [],
    'price': 00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
}
