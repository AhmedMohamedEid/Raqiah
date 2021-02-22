# -*- coding: utf-8 -*-

{
    'name': 'Pioneer_Appointment_Management',
    'version': '12.0.1.0.0',
    'summary': 'Pioneer_Appointment_Management',
    "description": """
      Pioneer_Appointment_Management
    """,
    'author': 'RN, pioneer solutions ',
    'company': 'Pioneer Solutions',
    'website': 'https://www.ps-sa.net',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'data/ir_sequence.xml',
        'views/pr_partner_appointment.xml',
        'security/ps_security_menuitem.xml',

    ],
    'images': ['static/description/icon.jpg'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
