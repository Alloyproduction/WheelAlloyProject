# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'CRM Claim Management',
    'version': '12.0.0.3',
    'category': 'Sales',
    'author': "BrowseInfo",
    'website': 'www.browseinfo.in',
    'sequence': 5,
    'summary': 'This plugin helps to manage after sales services as claim management',
    'description': "Claim system for your product, claim management, submit claim, claim form, Ticket claim, support ticket, issue, website project issue, crm management, ticket handling,support management, project support, crm support, online support management, online claim, claim product, claim services, issue claim, fix claim, raise ticket, raise issue, view claim, display claim, list claim on website ",
    'license':'OPL-1',
    'depends': ['crm','sale','sale_management','board'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/claim_cron_job.xml',
        'views/crm_claim_menu.xml',
        'views/res_partner_view.xml',
        'views/claim_dashboard.xml',
        'views/email_template.xml',
        'Report/profial.xml',
        'Report/claim_report.xml',
    ],
    'qweb': [
        "static/src/xml/claim_dashboard.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence':1,
    "images":["static/description/icon.png"],
}
