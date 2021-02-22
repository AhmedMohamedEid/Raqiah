# -*- coding: utf-8 -*-

{
    'name': 'pioneer Leave Management',
    'version': '12.0',
    'author': "Arun, Pioneer Solution",
    'category': 'Human Resources',
    'sequence': 28,
    'summary': 'Holidays, Allocation and Leave Requests According To Saudi Rules',
    'website': 'http://www.ps-sa.net',
    'depends': ['hr',  'hr_contract', 'hr_holidays', 'calendar', 'resource'
        , 'hr_overtime_ps'],
    'data': [
        'security/security.xml',
        'data/data.xml',
        'views/menu_view.xml',
        'views/hr_view.xml',
        'views/config_view.xml',
        'views/hr_holidays_saudi_view.xml',
        'views/hr_holidays_view.xml',
        'wizard/update_used_vacation_view.xml',
        'security/ir.model.access.csv',
        'security/ps_security_rules.xml',
        'security/ps_hl_security_menu.xml',
        'report/report.xml',
        'report/report_hr_holidays_saudi.xml',
        'views/hr_res_config.xml',
        'security/ps_hl_security_menu.xml'

        ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
