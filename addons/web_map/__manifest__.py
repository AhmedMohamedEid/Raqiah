# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Web Map',
    'category': 'Website',
    'version': '12.0.1.0.0',
    'author': 'CodUP',
    'summary': 'Map widget',
    'description': """Google Maps widget""",
    'depends': ['base','base_setup','web'],
    'data': [
        'views/web_map_templates.xml',
        'views/res_config_views.xml',
    ],
     'images': [
        'static/description/icon.png'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
