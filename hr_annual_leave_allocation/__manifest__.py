# -*- coding: utf-8 -*-
{
    'name': "End Of Service",
    'summary': """
        End Of Service""",
    'description': """
        End Of Service
    """,
    'author': "Magdy salah",
    'category': 'hr',
    'version': '0.12',
    'depends': ['hr', 'hr_contract', 'hr_holidays', 'hr_payroll','hr_payroll_account'],
    'data': [
        'security/ir.model.access.csv',
        'views/allocation_setting.xml',
        'views/hr_employee.xml',
        'views/end_of_service_award.xml',
        'report/eos_report.xml',
        'data/end_rule.xml',
    ],
}
