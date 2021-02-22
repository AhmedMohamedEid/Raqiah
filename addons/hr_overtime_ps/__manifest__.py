# -*- coding: utf-8 -*-

{
    'name': 'OverTime Management',
    'version': '11.0',
    'author': "Mani, Pioneer Solution",
    'category': 'Human Resources',
    'sequence': 28,
    'website': 'http://www.ps-sa.net',
    'depends': ['hr_contract', 'decimal_precision', 'hr_payroll', 'pioneer_HR_Employee'],
    'data': [
        
        'data/sequence.xml',
        'security/hr_security_menuitem.xml',
        'data/data.xml',
        'views/model_view.xml',
        'views/hr_contract_view.xml',
        'security/ir.model.access.csv',
        
        ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
