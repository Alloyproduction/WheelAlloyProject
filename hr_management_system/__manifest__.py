# -*- coding: utf-8 -*-
{
    'name': "HR Management System",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Mohammed Alwasefy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr','hr_contract','product','hr_payroll'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/data.xml',
        'views/hr_employee.xml',
        'views/hr_insurance.xml',
        'views/hr_protection.xml',
        'views/hr_mandate.xml',
        'views/hr_ticket.xml',
        'views/hr_contract_inherit.xml',
        'views/hr_salary_report.xml',
        'views/hr_salary_report_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
