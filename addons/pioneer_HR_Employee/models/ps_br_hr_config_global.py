# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
import time
import re
from odoo.tools import float_compare, float_is_zero

EXPIRY_TYPE = [('iqama', 'Iqama / National ID'), ('license', 'License'), ('passport', 'Passport'),
                             ('visa', 'Visa'), ('work_permit', 'Work Permit'), ('medical_insurance', 'Meical Insurance'),
                             ('other', 'Others')]
def get_email_from(self):
    UID_ROOT = 1
    email_from = self.env['res.users'].sudo().browse(UID_ROOT).login
    mail_server_ids = self.env['ir.mail_server'].sudo().search([('smtp_user','!=',False)])
    if mail_server_ids:
        email_from = self.env['ir.mail_server'].sudo().browse(mail_server_ids[0].id).smtp_user
    return email_from

def button_send_mail(self, email_to, subject, body_html):
    main_content = {
        'subject': subject,
        'author_id': self.env.user.partner_id.id,
        'body_html': body_html,
        'email_to': email_to,
    }
    self.env['mail.mail'].create(main_content).send()

def get_url(self, model):
    cr = self._cr
    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    database_name = cr.dbname
    object_ids = self.search([],limit=1)
    object_id = object_ids and object_ids.id or False
    url = ''
    if object_id:
        url = '%s/?db=%s#id=%s&view_type=form&model=hr.employee.loan.ps&menu_id=&action=' % (base_url, database_name, object_id)
    return url

def return_employee_domain(self, context, dom):
    user = self.env.user
    uid = self.env.uid
    is_direct_manager = False
    is_coach = False
    emp_obj = self.env['hr.employee']
    group_user = self.user_has_groups('base.group_user')
    group_hr_user = self.user_has_groups('hr.group_hr_user')
    group_hr_manager = self.user_has_groups('hr.group_hr_manager')
    group_hr_general_manager = self.env.user.has_group('pioneer_HR_Employee.group_hr_general_manager')

    # group_direct_manager_fig = user.has_group('base.group_direct_manager_fig')
    # if group_direct_manager_fig:
    #     is_direct_manager = True
    # DIRECT MANAGER
    if context.get('my_dm_loan_request', False):
        is_direct_manager = True
    manager_ids = emp_obj.sudo().search([('parent_id.user_id','=',uid)])
    if len(manager_ids):
        is_direct_manager = True
    if is_direct_manager:
        dom = ['|', ('user_id', '=', uid), ('parent_id.user_id', '=', uid)]

    # COACH
    if context.get('is_coach_form', False):
        is_coach = True
    coach_ids = emp_obj.sudo().search([('coach_id.user_id', '=', uid)])
    if len(coach_ids):
        is_coach = True
    if is_coach:
        dom = ['|', ('user_id', '=', uid), ('coach_id.user_id', '=', uid)]

    # COACH AND DIRECT MANAGER
    if is_coach and is_direct_manager:
        if context.get('is_coach_form', False):
            dom = ['|', ('user_id', '=', uid), ('coach_id.user_id', '=', uid)]
        if context.get('my_dm_loan_request', False):
            dom = ['|', ('user_id', '=', uid), ('parent_id.user_id', '=', uid)]

    if is_direct_manager and not context.get('my_dm_loan_request', False)\
            and (group_hr_user or group_hr_manager or group_hr_general_manager) :
        dom = [(1, '=', 1)]
    if is_direct_manager and not context.get('my_dm_loan_request', False) \
            and (group_hr_user or group_hr_manager or group_hr_general_manager) :
        dom = [(1, '=', 1)]
    print ('vvvv',dom)
    return dom

def mail_create(obj, email_from, email_to, subject, body):
    mail_mail = obj.env['mail.mail']
    mail_ids = []
    mail_ids.append(mail_mail.sudo().create({
                    'email_from': email_from,
                    'email_to': email_to,
                    'subject': subject,
                    'body_html': '<pre>%s</pre>' % body}))
    mail_mail.sudo().send(mail_ids)
    return True

def get_email_from(obj):
    UID_ROOT = 1
    email_from = obj.env['res.users'].sudo().browse(UID_ROOT).login
    mail_server_ids = obj.env['ir.mail_server'].sudo().search([('smtp_user','!=',False)])
    if mail_server_ids:
        email_from = obj.env['ir.mail_server'].sudo().browse(mail_server_ids[0].id).smtp_user
    return email_from


def get_config(obj):
    config = {}
    config_ids = obj.env['hr.leave.config.settings'].sudo().search([])
    if config_ids:
        config = config_ids[-1]
    return config
