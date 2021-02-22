
{
    'name': "HR Employee Customization",
    'summary': """
        a. Leave Management
        b. End of Service Benefits (EOSB)
        c. Overtime Request
        d. Loan and Advance
        e. Business Trip
        f. Employee Clearance""",

    'description': """
        Long description of module's purpose""",
    'purpose' : "http://ps-sa.net/web#id=579&view_type=form&model=project.task&menu_id=93&action=143",
    'author': "Arun, Pioneer Solutions",
    'website': "www.ps-sa.net",
    'category': 'Uncategorized',
    'version': '12.0',
    'depends': ['base', 'hr', 'hr_payroll', 'hr_contract'],

    'data': [
        'security/ps_br_ir_rule.xml',
        'security/ps_br_security_groups.xml',
        'security/ir.model.access.csv',
        'views/ps_br_res_users.xml',
        'views/ps_br_res_company.xml',
        'views/ps_br_hr_employee_expiry_details.xml',
        'views/ps_br_hr_employee_main.xml',
        'views/ps_br_hr_employee_mydetails.xml',
        # 'views/ps_br_hr_contract_view.xml',
        'views/ps_br_res_partner.xml',
        # 'wizard/ps_br_expiry_details.xml',

        'data/ps_br_ir_sequence.xml',
        'data/ps_br_mail_template_data.xml',
        'data/ps_br_scheduler.xml',
        'security/ps_security_menuitem.xml',

    ],
}
