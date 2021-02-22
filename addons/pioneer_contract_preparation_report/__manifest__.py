# -*- coding: utf-8 -*-
{
    'name': 'Contract preparation Report',
    'version': '12.0.0.0',
    'summary': 'Contract preparation Report',
    'description': 'Contract preparation Report',
    'category': 'account',
    'author': 'Mostafa Abbas',
    'website': 'ps-sa.net',
    'depends': ['base','base', 'crm', 'hr','granite_measurement'],
    'data': [
        'views/contract_preparation_view.xml',
        'reports/contract_preparation_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}