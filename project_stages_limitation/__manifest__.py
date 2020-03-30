# -*- coding: utf-8 -*-
{
    'name': "Project stage limitation",
    'summary': """Project stage limitation""",
    'description': """Project stage limitation""",
    'author': "Magdy, helcon",
    'website': "http://www.yourcompany.com",
    'category': 'Project',
    'version': '0.1',
    'depends': ['project', 'web_digital_sign','sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_users.xml',
        'views/project_task.xml',
    ],
}
