# -*- coding: utf-8 -*-
{
    'name': 'Manufaturing Granite',
    'summary': """Granite Measurement""",
    'version': '12.0.1.0.0',
    'author': 'Arunagiri',
    'website': "http://ps-sa.net",
    'company': ' Pioneer Solutions',
    "category": "Manufaturing",
    'depends': ['base', 'crm', 'hr', 'sale_crm','sale'],
    'data': [
             'security/ps_security_groups.xml',
             'views/ps_res_users.xml',
             'security/ir.model.access.csv',
             'views/granite_measurement_views.xml',
             'views/design_confirmation_views.xml',
             'views/material_detail_views.xml',
             'views/contract_preparation_views.xml',
             'views/manufaturing_installation_process_views.xml',
             'views/booking_for_installation_views.xml',
             'menu/menu.xml'

             ],
    'demo': [
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
