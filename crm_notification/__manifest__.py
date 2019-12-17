# -*- coding: utf-8 -*-
{
    'name': "crm_notification",

    'summary': """
       CRM Notification upon Lead,Qualified, Quotation, Won/Lost""",

    'description': """,
        Long description of module's purpose
    """,

    'author': "Telenoc",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.4',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','sale','sale_management','mail'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/views.xml',
        'security/security.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
