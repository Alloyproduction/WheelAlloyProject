# -*- coding: utf-8 -*-
{
    'name': "Techician Request",

    'summary': """
        This Module make the employee request for Material from inventory internaly  and send mail notification to manager """,

    'description': """
        Internal Request of Material by Employees
        You can select Multiple Products at once 
        Send Mail as notification to the Employee and manager
        Create internal transfer to the employee 

    """,

    'author': "Haytham El Sayed",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','stock','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/technicianseq.xml',
     'security/technician_request_security.xml',
        'views/views.xml',
        'views/stockpickview.xml',
        'views/technicianView.xml',
        'views/templates.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
'installable': True,
    'application':True,
    'sequence':10,
}