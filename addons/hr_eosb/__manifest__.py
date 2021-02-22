# -*- coding: utf-8 -*-
{
    'name': 'HR EOSB',
    'version': '12.0',
    'category': 'Human Resources',
    'description': "",
    'author': "Mani, Pioneer Solution",
    'migrated' : 'Arun, Pioneer Solution',
    'depends': ['base','hr_contract', 'account', 'contacts', 'hr_payroll'],
    'data': [
        'views/hr_view.xml',
        'views/hr_payroll_view.xml',
        'views/model_view.xml',
        # 'views/workflow.xml',
        'views/res_company.xml',
        'report/report.xml',
        'report/report_eosb_eosb.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'security/ps_security_menuitem.xml',


            ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
