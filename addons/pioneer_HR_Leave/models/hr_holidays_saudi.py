# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime,timedelta
from lxml import etree, html

import math
import collections
# try:
#     from service_solutions.common_ps.models.nazar import mail_create, get_email_from, get_config
# except:
#     try:
#         from odoo.common_ps.models.nazar import mail_create, get_email_from, get_config
#     except:
#         from odoo.addons.common_ps.models.nazar import mail_create, get_email_from, get_config

from odoo import SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from odoo.addons.pioneer_HR_Employee.models import ps_br_hr_config_global as hg


class hr_holidays_type_saudi(models.Model):
    _name = 'hr.holidays.type.saudi'
    _inherit = ['mail.thread']


    name = fields.Char(string='Name', required=True, translate=True, readonly=False, states={'active': [('readonly', True)],'inactive': [('readonly', True)],} )
    one_time_leave = fields.Boolean(string='One Time Leave', readonly=False, states={'active': [('readonly', True)],'inactive': [('readonly', True)],} )
    female_only = fields.Boolean(string='Applicable for Female Only', readonly=False, states={'active': [('readonly', True)],'inactive': [('readonly', True)],} )
    deduction_type = fields.Selection([('full_paid','Full Paid'),('deduct_salary','Deduct From Salary'),('deduct_leave','Deduct From Leave'), ('deduct_ot','Deduct From OT'), ('deduct_salary_leave','Deduct From Salary and Leave'),], string='Deduction Type', required=True, readonly=False, states={'active': [('readonly', True)],'inactive': [('readonly', True)],} )
    max_days_limit = fields.Integer(string='Maximum Days Limit', readonly=False, states={'active': [('readonly', True)],'inactive': [('readonly', True)],} )

    salary_rule_line = fields.One2many('hr.holidays.type.salary.rule.saudi', 'type_id', string='Salary Lines', copy=True, readonly=False, states={'active': [('readonly', True)],'inactive': [('readonly', True)],} )
    leave_rule_line = fields.One2many('hr.holidays.type.leave.rule.saudi', 'type_id', string='Leave Lines', copy=True, readonly=False, states={'active': [('readonly', True)],'inactive': [('readonly', True)],} )
    ot_rule_line = fields.One2many('hr.holidays.type.ot.rule.saudi', 'type_id', string='OT Lines', copy=True, readonly=False, states={'active': [('readonly', True)],'inactive': [('readonly', True)],} )
    is_annual = fields.Boolean("Annual Vacation")

    state = fields.Selection([
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ],
            'Status', readonly=True, track_visibility='onchange', default='draft')

    @api.multi
    def unlink(self):
        for record in self:
            if record.state not in ('draft'):
                raise Warning(_('You cannot delete an holidays type which is not draft.'))
        return models.Model.unlink(self)

    @api.multi
    def validate_lines(self, records, msg):
        temp = 0
        for line in records:
            if temp >= line.days:raise except_orm(_('Invalid Value !'), _(msg))
            temp = line.days
        return True

    @api.multi
    def action_active(self):
        temp = 0
        records = {}
        if self.deduction_type == 'deduct_salary':
            self.validate_lines(self.salary_rule_line, 'Pay Rule days should be ascending')
        elif self.deduction_type == 'deduct_leave':
            self.validate_lines(self.leave_rule_line, 'Leave Rule days should be ascending')
        elif self.deduction_type == 'deduct_ot':
            self.validate_lines(self.ot_rule_line, 'OT Rule hours should be ascending')
        elif self.deduction_type == 'deduct_salary_leave':
            self.validate_lines(self.salary_rule_line, 'Pay Rule days should be ascending')
            self.validate_lines(self.leave_rule_line, 'Leave Rule days should be ascending')
        return self.write({'state': 'active'})

    @api.multi
    def action_inactive(self):
        return self.write({'state': 'inactive'})

    @api.multi
    def action_reactive(self):
        return self.write({'state': 'active'})

    @api.multi
    @api.onchange('deduction_type')
    def onchange_deduction_type(self):
        return {'value': {'max_days_limit': 0}}

class hr_holidays_type_salary_rule_saudi(models.Model):
    _name = 'hr.holidays.type.salary.rule.saudi'
    _inherit = ['mail.thread', 'resource.mixin']

    type_id = fields.Many2one('hr.holidays.type.saudi', string='Type Reference', ondelete='cascade', index=True)
    days = fields.Float(string='Days', required=True)
    percentage = fields.Float(string='Deduction Days', required=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ],
            'Status', readonly=True, track_visibility='onchange', default='draft')

class hr_holidays_type_leave_rule_saudi(models.Model):
    _name = 'hr.holidays.type.leave.rule.saudi'
    _inherit = ['mail.thread', 'resource.mixin']

    type_id = fields.Many2one('hr.holidays.type.saudi', string='Type Reference', ondelete='cascade', index=True)
    days = fields.Float(string='Days', required=True)
    percentage = fields.Float(string='Deduction Days', required=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ],
            'Status', readonly=True, track_visibility='onchange', default='draft')

class hr_holidays_type_ot_rule_saudi(models.Model):
    _name = 'hr.holidays.type.ot.rule.saudi'
    _inherit = ['mail.thread', 'resource.mixin']

    type_id = fields.Many2one('hr.holidays.type.saudi', string='Type Reference', ondelete='cascade', index=True)
    days = fields.Float(string='Hours', required=True)
    percentage = fields.Float(string='Deduction Hours', required=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ],
            'Status', readonly=True, track_visibility='onchange', default='draft')


class hr_leave(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def _get_employee(self):
        result = False
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if employee_ids:
            result = employee_ids[0]
        return result

    @api.multi
    @api.depends('write_date','employee_id','is_direct_hrm_approve')
    def _get_current_user(self):
        for case in self:
            state = case.state
            is_direct_manager = False
            is_coach = False
            is_show_confirm = False
            is_show_hrm_approve = False
            employee = case.employee_id.sudo()
            parent = employee.parent_id.sudo()
            group_hr_manager = case.env.user.has_group('hr.group_hr_manager')
            if (employee and parent and parent.user_id) and parent.user_id.id == case.env.uid:
                is_direct_manager = True
                if state == 'request':
                    is_show_confirm = True
            if (employee and employee.coach_id and employee.coach_id.user_id) and employee.coach_id.user_id.id == case.env.uid:
                is_coach = True
                if state == 'request':
                    is_show_confirm = True
            if state == 'request' and (is_coach or is_direct_manager) :
                is_show_confirm = True
            if case.is_direct_hrm_approve :
                if state == 'request':
                    if group_hr_manager:
                        is_show_hrm_approve = True
            if state == 'confirm':
                if group_hr_manager:
                    is_show_hrm_approve = True
            case.is_direct_manager = is_direct_manager
            case.is_coach = is_coach
            case.is_show_confirm = is_show_confirm
            case.is_show_hrm_approve = is_show_hrm_approve
#http://stackoverflow.com/questions/14288498/creating-a-loop-for-two-dates
#http://stackoverflow.com/questions/2161752/how-to-count-the-frequency-of-the-elements-in-a-list

    def date_range(self, start, end):
        r = (end+timedelta(days=1)-start).days
        return [start+timedelta(days=i) for i in range(r)]

    def make_unique(self, original_list):
        unique_list = []
        # map(lambda x: unique_list.append(x) if (x not in unique_list) else False, original_list)
        for x in original_list:
            if x not in unique_list:
                unique_list.append(x)
        return unique_list

    def _get_official_leave_dates(self):
        DATE_FORMAT = "%Y-%m-%d"
        array_date = []
        official_leave_ids = self.env['hr.official.holidays.saudi'].search([('state', '=', 'approve')])
        for official_leave_id in official_leave_ids:
            date_from_official_leave = official_leave_id.date_from.date()
            date_to_official_leave = official_leave_id.date_to.date()
            array_date += self.date_range(date_from_official_leave.date(), date_to_official_leave.date())
        return self.make_unique(array_date)


    def _get_official_leave(self, date_from, date_to, DATETIME_FORMAT):
        request_leave_dates = self.date_range(date_from, date_to)
        result = [item for item in request_leave_dates if item in self._get_official_leave_dates()]
        return len(result) or 0, result

    def _compute_official_leave(self, date_from, date_to, DATETIME_FORMAT):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        lenresult, result = self._get_official_leave(date_from, date_to, DATETIME_FORMAT)
        return lenresult

    def _compute_weekend_leave(self, contract_id, date_from, date_to, DATETIME_FORMAT):
        attendance_id = []
        attendance_id_unique = []
        result_array = []
        result = 0
        req_off_remianing_dates = []
        if contract_id:
            lenofficial_leave, official_leave = self._get_official_leave(date_from, date_to, DATETIME_FORMAT)
            request_leave_dates = self.date_range(date_from, date_to)
            req_off_remianing_dates = [item for item in request_leave_dates if item not in official_leave]

            if contract_id.resource_calendar_id:
                attendance_ids = self.env['resource.calendar.attendance'].search([('calendar_id', '=', contract_id.resource_calendar_id.id)])
                for attendance in attendance_ids:
                    attendance_id += attendance.dayofweek
                for i in req_off_remianing_dates:
                    weekday = i.weekday()
                    uattendance_id = self.make_unique(attendance_id)
                    if str(weekday) not in uattendance_id:
                        result += 1

        return result


    @api.one
    @api.depends('date_from', 'date_to', 'employee_id', 'contract_id','leave_type_id')
    def _compute_leave_days(self):
        days = weekend_leave_days = 0
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if self.date_from and self.date_to:
            days, months, years = self.env['hr.employee']._compute_date(self.date_from, self.date_to, DATETIME_FORMAT)
            self.request_leave_days = days + 1
            self.official_leave_days = self._compute_official_leave(self.date_from, self.date_to, DATETIME_FORMAT)
            if self.contract_id:
                weekend_leave_days = self._compute_weekend_leave(self.contract_id, self.date_from, self.date_to, DATETIME_FORMAT)
                self.weekend_leave_days = weekend_leave_days
            official_leaves = self._compute_official_leave(self.date_from, self.date_to, DATETIME_FORMAT)
            print ('ffff', self.name, days, official_leaves, weekend_leave_days)
            self.actual_leave_days = (days + 1) - (official_leaves + weekend_leave_days)
            self.cancel_leave_days = 0

    @api.one
    @api.depends('employee_id','leave_type_id', 'date_from', 'date_to')
    def _get_employee_details(self):
        employee = self.employee_id.sudo()
        self.department_id = employee.department_id.id or False
        self.job_id = employee.job_id.id or False
        self.aj_date = employee.aj_date
        self.accumlate_days = employee.accumlate_days
        self.used_leave = employee.used_leave
        self.deduction_type = self.leave_type_id.deduction_type
        # deduction = employee.leave_compute(employee.id, self.date_from, self.date_to, ['deduct_salary', 'deduct_salary_leave'])
        # print('ccccccc', deduction)
        self.balance_leave = employee.balance_leave

    @api.one
    @api.depends('leave_type_id', 'date_from', 'date_to')
    def _compute_exceeded_leave_days(self):
        self.exceeded_leave_days = 0
        if self.leave_type_id.max_days_limit > 0:self.exceeded_leave_days = self.actual_leave_days - self.leave_type_id.max_days_limit



#    def _get_deduct_values(self, deduction_type, records, key_value):
#        vals = 0
#        percentage = 0
#        temp = 0
#        temp_leave = key_value
#        for line in records:
#            if temp_leave > 0:
#                if temp_leave > (line.days - temp):
#                    if deduction_type == 'deduct_salary':vals += ((self.contract_id.wage / 30) * (line.days - temp)) * line.percentage / 100
#                    elif deduction_type in ('deduct_leave', 'deduct_ot'):vals += (line.days - temp) * line.percentage
#                else:
#                    if deduction_type == 'deduct_salary':vals += ((self.contract_id.wage / 30) * temp_leave) * line.percentage / 100
#                    elif deduction_type in ('deduct_leave', 'deduct_ot'):vals += temp_leave * line.percentage
#                temp_leave = temp_leave - line.days
#                temp += line.days
#                percentage = line.percentage
#        return vals, temp_leave, percentage

    def _get_deduct_values(self, deduction_type, records, key_value):
        vals, temp = 0, 0
        percentage = 1
        temp_leave = key_value
        for line in records:
            if temp_leave > 0:
                if temp_leave > (line.days - temp):
                    vals += (line.days - temp) * line.percentage
                else:
                    vals += temp_leave * line.percentage
                temp_leave = temp_leave - (line.days - temp)
                temp += (line.days - temp)
                percentage = line.percentage
        return vals, temp_leave, percentage


    @api.one
    @api.depends('employee_id', 'contract_id', 'leave_type_id', 'date_from', 'date_to', 'deductable_hours')
    def _compute_deduct_values(self):
        vals = 0
        if self.leave_type_id and self.contract_id:
            if self.leave_type_id.deduction_type == 'deduct_salary':
                vals, temp_leave, percentage = self._get_deduct_values('deduct_salary', self.leave_type_id.salary_rule_line, self.actual_leave_days)
                self.deductable_amount = (vals + (temp_leave * percentage)) * (self.contract_id.wage / 30)

            elif self.leave_type_id.deduction_type == 'deduct_leave':
                vals, temp_leave, percentage = self._get_deduct_values('deduct_leave', self.leave_type_id.leave_rule_line, self.actual_leave_days)
                self.deductable_days = vals + (temp_leave * percentage)

            elif self.leave_type_id.deduction_type == 'deduct_ot':
                vals, temp_leave, percentage = self._get_deduct_values('deduct_ot', self.leave_type_id.ot_rule_line, self.ot_hours)
                self.deductable_hours = vals + (temp_leave * percentage)
            elif self.leave_type_id.deduction_type == 'deduct_salary_leave':
                vals, temp_leave, percentage = self._get_deduct_values('deduct_salary', self.leave_type_id.salary_rule_line, self.actual_leave_days)
                self.deductable_amount = (vals + (temp_leave * percentage)) * (self.contract_id.wage / 30)
                vals, temp_leave, percentage = self._get_deduct_values('deduct_leave', self.leave_type_id.leave_rule_line, self.actual_leave_days)
                self.deductable_days = vals + (temp_leave * percentage)



#    @api.one
#    @api.depends('employee_id', 'contract_id', 'leave_type_id', 'date_from', 'date_to')
#    def _compute_deductable_amount(self):
#        vals = 0
#        if (self.leave_type_id and self.contract_id) and self.leave_type_id.deduction_type in ('deduct_salary', 'deduct_salary_leave'):
#            self.deductable_amount = (self.contract_id.wage / 30) * self.actual_leave_days
#            if self.leave_type_id.salary_rule_line:
#                temp_leave = self.actual_leave_days
#                for line in self.leave_type_id.salary_rule_line:
#                    if temp_leave > 0:
#                        if self.actual_leave_days > line.days:
#                            vals += ((self.contract_id.wage / 30) * line.days) * line.percentage / 100
#                        else:
#                            vals += ((self.contract_id.wage / 30) * temp_leave) * line.percentage / 100
#                    temp_leave = temp_leave - line.days
#                vals += (self.contract_id.wage / 30) * temp_leave
#                self.deductable_amount = vals

#    @api.one
#    @api.depends('employee_id', 'contract_id', 'leave_type_id', 'date_from', 'date_to')
#    def _compute_deductable_days(self):
#        vals = 0
#        if (self.leave_type_id and self.contract_id) and self.leave_type_id.deduction_type in ('deduct_leave', 'deduct_salary_leave'):
#            self.deductable_amount = self.actual_leave_days
#            if self.leave_type_id.leave_rule_line:
#                temp_leave = self.actual_leave_days
#                for line in self.leave_type_id.leave_rule_line:
#                    if temp_leave > 0:
#                        if self.actual_leave_days > line.days:
#                            vals += line.days * line.percentage
#                        else:
#                            vals += line.days * temp_leave
#                    temp_leave = temp_leave - line.percentage
#                vals += temp_leave
#                self.deductable_days = vals

    # @api.multi
    # @api.depends('employee_id')
    # def get_allowed_employees(self):
    #     for case in self:
    #         allowed_employee_ids =
    #         case.allowed_employee_ids = allowed_employee_ids

    name = fields.Char(string='Description', readonly=False, states={'approve': [('readonly', True)],'cancel': [('readonly', True)],'refuse': [('readonly', True)]} )
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=False,
                                  states={'approve': [('readonly', True)], 'cancel': [('readonly', True)],
                                          'refuse': [('readonly', True)]}, default=_get_employee)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=False, readonly=False, states={'approve': [('readonly', True)],'cancel': [('readonly', True)],'refuse': [('readonly', True)],})
    department_id = fields.Many2one('hr.department', string='Department', store=True, readonly=True, compute='_get_employee_details')
    job_id = fields.Many2one('hr.job', string='Job', store=True, readonly=True, compute='_get_employee_details')
    date_from = fields.Datetime(string='Start Date', required=True, readonly=False, states={'approve': [('readonly', True)],'cancel': [('readonly', True)],'refuse': [('readonly', True)]})
    date_to = fields.Datetime(string='End Date', required=True, readonly=False, states={'approve': [('readonly', True)],'cancel': [('readonly', True)],'refuse': [('readonly', True)]})
    request_leave_days = fields.Integer(string='Request Days', readonly=True, compute='_compute_leave_days')
    official_leave_days = fields.Integer(string='Official Leave Days', readonly=True, compute='_compute_leave_days')
    weekend_leave_days = fields.Integer(string='Weekend Leave Days', readonly=True, compute='_compute_leave_days')
    actual_leave_days = fields.Integer(string='Actual Leave Days', readonly=True, compute='_compute_leave_days')
    cancel_leave_days = fields.Integer(string='Actual Leave Days', readonly=True, compute='_compute_leave_days')
    request_date = fields.Datetime(string='Request Date', readonly=False)
    leave_type_id = fields.Many2one('hr.holidays.type.saudi', string='Leave Type', required=False, readonly=False, states={'approve': [('readonly', True)],'cancel': [('readonly', True)],'refuse': [('readonly', True)]})

    allow_one_time_leave = fields.Boolean(string='Allow One Time Leave Again', default=False, readonly=False,
                                          states={'approve': [('readonly', True)], 'cancel': [('readonly', True)],
                                                  'refuse': [('readonly', True)]})
    allow_max_days_limit = fields.Boolean(string='Allow Exceeding Maximum Days Limit', default=False, readonly=False,
                                          states={'approve': [('readonly', True)], 'cancel': [('readonly', True)],
                                                  'refuse': [('readonly', True)]})
    excuse_salary_deduction = fields.Boolean(string='Excuse Salary Deduction', default=False, readonly=False,
                                             states={'approve': [('readonly', True)], 'cancel': [('readonly', True)],
                                                     'refuse': [('readonly', True)]})
    excuse_leave_deduction = fields.Boolean(string='Excuse Leave Deduction', default=False, readonly=False,
                                            states={'approve': [('readonly', True)], 'cancel': [('readonly', True)],
                                                    'refuse': [('readonly', True)]})
    excuse_ot_deduction = fields.Boolean(string='Excuse OverTime Deduction', default=False, readonly=False,
                                         states={'approve': [('readonly', True)], 'cancel': [('readonly', True)],
                                                 'refuse': [('readonly', True)]})
    execute_with_negative_leave = fields.Boolean(string='Execute With Negative Leave', default=False, readonly=False,
                                                 states={'approve': [('readonly', True)],
                                                         'cancel': [('readonly', True)],
                                                         'refuse': [('readonly', True)]})

    exceeded_leave_days = fields.Integer(string='Warning !: Exceeded the maximum leave limit of the leave type with days of ', readonly=True, compute='_compute_exceeded_leave_days')
    aj_date = fields.Date(compute="_get_employee_details", string='Actual Date of Joined')
    accumlate_days = fields.Float(compute="_get_employee_details", string='Accumulated Leave')
    used_leave = fields.Float(compute="_get_employee_details", string='Used Leave')
    deduction_type = fields.Selection(
        [('full_paid', 'Full Paid'), ('deduct_salary', 'Deduct From Salary'), ('deduct_leave', 'Deduct From Leave'),
         ('deduct_ot', 'Deduct From OT'), ('deduct_salary_leave', 'Deduct From Salary and Leave'), ],
        compute="_get_employee_details")
    deductable_amount = fields.Float(string='Deductable Amount', readonly=True, compute='_compute_deduct_values')
    deductable_days = fields.Float(string='Deductable Days', readonly=True, compute='_compute_deduct_values')
    deductable_hours = fields.Float(string='Deductable Hours', readonly=True, compute='_compute_deduct_values')
    balance_leave = fields.Float('Balance Leaves', compute="_get_employee_details")
    ot_hours = fields.Float(string='OverTime Hours', readonly=False, states={'approve': [('readonly', True)],'cancel': [('readonly', True)],'refuse': [('readonly', True)]})
    contact = fields.Char(string='Contact During Vacation', readonly=False,
                           states={'approve': [('readonly', True)], 'cancel': [('readonly', True)], })
    eremployee = fields.Selection([('exit', 'Exit'), ('reentry', 'Re-Entry')], 'Employee', readonly=False,
                                   states={'approve': [('readonly', True)], 'cancel': [('readonly', True)], })
    erfamily = fields.Selection([('exit', 'Exit'), ('reentry', 'Re-Entry')], 'Family', readonly=False,
                                 states={'approve': [('readonly', True)], 'cancel': [('readonly', True)], })

    is_direct_manager = fields.Boolean(string='Is Direct Manager', readonly=True,
                                       compute='_get_current_user')
    is_coach = fields.Boolean(string='Is Coach', default=False, readonly=True, compute='_get_current_user')
    is_show_confirm = fields.Boolean(string='Is Show Confirm Button', readonly=True,
                                     compute='_get_current_user')
    is_show_hrm_approve = fields.Boolean(string='Is Show HR-Manager Approval Button', readonly=True,
                                     compute='_get_current_user')
    is_direct_hrm_approve = fields.Boolean('HR Manager override the direct manager approval', copy=False
                                , default=False
                                , readonly=False, states={'approve': [('readonly', True)], 'cancel': [('readonly', True)], })
    cancel_by = fields.Many2one('res.users', string='Cancelled By', readonly=True,)
    cancel_date = fields.Datetime(string='Cancel Date', readonly=True,)
    refused_by = fields.Many2one('res.users', string='Refused By', readonly=True,)
    refused_date = fields.Datetime(string='Refused Date', readonly=True,)
    direct_manager_id = fields.Many2one('res.users', string='Direct Manager', readonly=True)
    direct_manager_date = fields.Datetime(string='Confirmed Date', readonly=True)
    direct_manager_note = fields.Text(string='Comments', readonly=True, states={'request': [('readonly', False)]})
    hr_manager_id = fields.Many2one('res.users', string='HR Manager', readonly=True)
    hr_manager_date = fields.Datetime(string='Confirmed Date', readonly=True)
    hr_manager_note = fields.Text(string='Comments', readonly=True, states={'confirm': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=False, states={'approve': [('readonly', True)],'cancel': [('readonly', True)],},
        default=lambda self: self.env['res.company']._company_default_get('hr.leave'))

    gm_manager_id = fields.Many2one('res.users', string='GM Manager', readonly=True)
    gm_manager_date = fields.Datetime(string='Confirmed Date', readonly=True)
    gm_manager_note = fields.Text(string='Comments', readonly=True, states={'confirm': [('readonly', False)]})
    remp_ids = fields.Many2one('hr.employee', string='Replacement Employee', readonly=False,
                                states={'approve': [('readonly', True)], 'cancel': [('readonly', True)], })

    note = fields.Html(string='Note', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
            ('draft', 'Draft'),
            ('request', 'Waiting for DM Approval'),
            ('confirm', 'Waiting for HR-Manager Approval'),
            # ('off_confirm','Confirmed'),
            ('approve', 'Approved'),
            # ('gm_approve', 'GM Approved'),
            ('refuse', 'Refused'),
            ('cancel', 'Cancel'),
            ],
            'Status', readonly=True, track_visibility='onchange', default='draft')
#    allowed_employee_ids = fields.Many2many('hr.employee', 'Allowed Employee', compute="get_allowed_employees", stroe=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(hr_leave, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        context = dict(self._context or {})
        doc = etree.XML(res['arch'])
        emp_obj = self.env['hr.employee']
        employee_ids = emp_obj.search([('user_id', '=', self.env.uid)])
        employee = employee_ids and employee_ids[0]
        for node in doc.xpath("//field[@name='employee_id']"):
            domain = hg.return_employee_domain(self, context, [])
            node.set('domain', str(domain))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    #OVERRIDEED
    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        is_coach = self.is_coach
        is_direct_manager = self.is_direct_manager
        for holiday in self:
            val_type = holiday.holiday_status_id.validation_type
            if state == 'confirm':
                continue

            if state == 'draft':
                if holiday.employee_id != current_employee and not is_manager:
                    raise UserError(_('Only a Leave Manager can reset other people leaves.'))
                continue

            # if not is_officer or not is_direct_manager or not is_coach:
            #     raise UserError(_('Only a direct Manager or HR officer or HR Manager can Approve or Refuse leave requests.'))
            #
            # if is_officer:
            #     # use ir.rule based first access check: department, members, ... (see security.xml)
            #     holiday.check_access_rule('write')

            # if holiday.employee_id == current_employee and not is_manager:
            #     raise UserError(_('Only a Leave Manager can approve its own requests.'))

            if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
                manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
                if (manager and manager != current_employee) and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                    raise UserError(_('You must be either %s\'s manager or Leave manager to approve this leave') % (holiday.employee_id.name))

            if state == 'validate' and val_type == 'both':
                if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                    raise UserError(_('Only an Leave Manager can apply the second approval on leave requests.'))

    @api.model
    def create(self, values):
        result = super(hr_leave, self).create(values)
        return result

    @api.multi
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        employee = False
        for case in self:
            employee = case.employee_id
        if not employee:
            return {'value': {'contract_id': False}}
        contract_ids = self.env['hr.contract'].search([('employee_id', '=', employee.id)], limit=1, order='date_start desc')
        return {'value': {'contract_id': contract_ids and contract_ids.id or False}}

    @api.multi
    def get_one_time_leave(self, employee_id, leave_type_id):
        return self.env['hr.leave'].search([('employee_id','=',employee_id.id), ('leave_type_id','=',leave_type_id.id), ('state','in',('approve','cancel'))])

    @api.multi
    def action_request(self):
        config = self.env['hr.leave.config.settings'].sudo()._get_values()
        employee = self.employee_id.sudo()
        parent = employee.parent_id.sudo()
        if config and employee and self.leave_type_id:
            if self.leave_type_id.is_annual and config.annual_leave_doj:
                year_bef = datetime.now() - relativedelta(years=1)

                if employee.joined_date and employee.joined_datez > year_bef:
                    raise Warning(_('You are not eligible to apply for Annual Leave!'))
                if not employee.aj_date:
                    raise Warning(_('You are not eligible to apply for Annual Leave!. Please enter joining date'))

            #for checking the validation for annual 5 days leave.
            #todo : how to check for one year
            if self.leave_type_id.is_annual and config.annual_leave:
                rec_ids = self.search([('leave_type_id.is_annual','=',True),
                                       ('employee_id','=',employee.id),
                                        ('id','!=',self.id)])
                total = sum([r.deductable_days for r in rec_ids])

                if total > 5 and self.deductable_days < 5:
                    raise Warning(_('Annual Vacation should be minimum 5 days'))

        if (employee and self.leave_type_id) and employee.gender != 'female' and self.leave_type_id.female_only:
                raise except_orm(_('Warining!'), _('This leave type strictly applicable only for female.'))
        if ((employee) and parent) and parent.work_email:
            email_from = hg.get_email_from(self)
            if email_from:
                subject = ("Leave request from employee of : '%s' ") % (employee.name)
                body = _("Hello,\n\n")
                body += _("Employee %s sent leave request at Date from %s to %s, Please take necessary steps..") % (employee.name,self.date_from,self.date_from)
                body += "--\n"
                hg.mail_create(self, email_from, parent.work_email, subject, body)
        return self.write({'state': 'request', 'request_date':datetime.now()})


    def action_confirm(self):
        config = hg.get_config(self)
        email_from = hg.get_email_from(self)
        employee = self.employee_id.sudo()
        if email_from:
            if config:
                for manager in config['managers_ids']:
                    subject = ("Leave request from Employee: '%s' ") % (employee.name)
                    body = _("Hello,\n\n")
                    body += _("Employee %s leave request was confirmed by his direct manager, And its waiting for your approval,Please take necessary steps..") % (employee.name)
                    body += "--\n"
                    if manager.work_email:hg.mail_create(self, email_from, manager.work_email, subject, body)
            if self.env.user.id == employee.user_id.id:
                raise UserError(_('You Cannot Confirm Your Own Request.'))
            if self.user_has_groups('base.group_user') and not (self.is_coach or self.is_direct_manager):
                raise UserError(_('Either Assigned Direct Manager or HR Manager Are Allowed To Confirm'))

            if employee.work_email:
                subject = ("Your leave request is waiting for HR Approval")
                body = _("Hello,\n\n")
                body += _("Your leave request was confirmed, And its waiting for Officer Approval..")
                body += "--\n"
                hg.mail_create(self, email_from, employee.work_email, subject, body)

        return self.write({'state': 'confirm'
                              , 'direct_manager_id': self.env.uid
                              , 'direct_manager_date': fields.date.today()
                           })

    # @api.multi
    # def action_confirm_off(self):
    #     config = hg.get_config(self)
    #     email_from = hg.get_email_from(self)
    #     employee = self.employee_id.sudo()
    #
    #     if email_from:
    #         if config:
    #             for manager in config.managers_ids:
    #                 subject = ("Leave request from Employee: '%s' ") % (employee.name)
    #                 body = _("Hello,\n\n")
    #                 body += _(
    #                     "Employee %s leave request was confirmed by officer, And its waiting for your approval,Please take necessary steps..") % (
    #                         employee.name)
    #                 body += "--\n"
    #                 if manager.work_email: hg.mail_create(self, email_from, manager.work_email, subject, body)
    #
    #         if employee.work_email:
    #             subject = ("Your leave request is waiting for HR Approval")
    #             body = _("Hello,\n\n")
    #             body += _("Your leave request was confirmed, And its waiting for HR Approval..")
    #             body += "--\n"
    #             hg.mail_create(self, email_from, employee.work_email, subject, body)
    #
    #     return self.write(
    #         {'state': 'off_confirm'})

    @api.multi
    def action_refuse(self):
        email_from = hg.get_email_from(self)
        employee = self.employee_id.sudo()
        parent = employee.parent_id.sudo()
        state = ''
        if self.state == 'request':state = 'by Direct Manager'
        elif self.state == 'confirm':state = 'by HR Manager'
        if email_from:
            if employee.work_email:
                subject = ("Your leave request was refused")
                body = _("Hello,\n\n")
                body += _("Your leave request was refused %s") % (state)
                body += "--\n"
                hg.mail_create(self, email_from, employee.work_email, subject, body)

            if ((employee) and parent) and parent.work_email and self.state=='confirm':
                subject = ("Leave request was refused for employee : '%s' ") % (employee.name)
                body = _("Hello,\n\n")
                body += _("Leave request was refused for employee : '%s' %s") % (employee.name, state)
                body += "--\n"
                hg.mail_create(self, email_from, parent.work_email, subject, body)

        return self.write({'state': 'refuse','refused_by': self.env.uid, 'refused_date': fields.date.today()})

    @api.multi
    def action_cancel(self):
        email_from = hg.get_email_from(self)
        employee = self.employee_id.sudo()
        parent = employee.parent_id.sudo()
        state = ''
        if self.state == 'request':
            state = 'by Direct Manager'
        elif self.state == 'confirm':
            state = 'by HR Manager'
        if email_from:
            if employee.work_email:
                subject = ("Your leave request was cancelled")
                body = _("Hello,\n\n")
                body += _("Your leave request was cancelled %s") % (state)
                body += "--\n"
                hg.mail_create(self, email_from, employee.work_email, subject, body)

            if ((employee) and parent) and parent.work_email and self.state == 'confirm':
                subject = ("Leave request was cancelled for employee : '%s' ") % (employee.name)
                body = _("Hello,\n\n")
                body += _("Leave request was cancelled for employee : '%s' %s") % (employee.name, state)
                body += "--\n"
                hg.mail_create(self, email_from, parent.work_email, subject, body)

        return self.write({'state': 'cancel', 'cancel_by': self.env.uid, 'cancel_date': fields.date.today()})


    @api.multi
    def action_approve(self):
        employee = self.employee_id.sudo()
        parent = employee.parent_id.sudo()
        amount = 0
        if not self.allow_one_time_leave and self.leave_type_id.one_time_leave and self.get_one_time_leave(employee,self.leave_type_id):
            raise except_orm(_('Warining!'), _('The Employee was already utilized the one time leave,Please Allow One Time Leave Again in HR Setting or Refuse.'))    

        if not self.allow_max_days_limit and self.exceeded_leave_days > 0:
            raise except_orm(_('Warining!'), _('The Leave is exceeding the maximum limit leave type,Please Allow Exceeding Maximum Days Limit in HR Setting or Refuse.')) 

        if self.leave_type_id.female_only and employee.gender != 'female':
            raise except_orm(_('Warining!'), _('This leave type strictly applicable only for female.'))   

        if not self.execute_with_negative_leave and self.leave_type_id.deduction_type in ('deduct_salary', 'deduct_salary_leave') and self.deductable_days > employee.balance_leave and not self.excuse_leave_deduction:
            raise except_orm(_('Warining!'), _('Balance leave is not enough,Please Execute With Negative Leave in HR Setting or Refuse.'))  
 

        if self.leave_type_id.deduction_type in ('deduct_salary', 'deduct_salary_leave') and not self.excuse_salary_deduction and self.deductable_amount > 0:
            amount = self.deductable_amount
        deduction_type = self.leave_type_id.deduction_type or ''
        if deduction_type == 'deduct_ot' \
                and not self.excuse_ot_deduction and self.deductable_hours > 0:
            amount = ((self.contract_id.wage / 30) / 8) * self.deductable_hours


        if amount > 0:               
            self.env['hr.holidays.deduction.summary.saudi'].create({
                    'employee_id': employee.id,
                    'leave_id': self.id,
                    'date': self.date_from,
                    'amount': amount,
                    'state': 'undeducted',
            })


        if self.leave_type_id.deduction_type in ('deduct_leave', 'deduct_salary_leave') \
                and not self.excuse_leave_deduction and self.deductable_days > 0:
            leave = employee.used_leave + self.deductable_days
            employee.write({'used_leave':leave})

        email_from = hg.get_email_from(self)
        if email_from:
            if ((employee) and parent) and parent.work_email:
                subject = ("Leave request was approved for employee : '%s' ") % (employee.name)
                body = _("Hello,\n\n")
                body += _("Leave request was approved for employee : '%s' by HR Manager") % (employee.name)
                body += "--\n"
                hg.mail_create(self, email_from, parent.work_email, subject, body)

            if (employee) and employee.work_email:
                subject = ("Your leave request was approved") 
                body = _("Hello,\n\n")
                body += _("Your leave request was approved by HR Manager . Waiting for GM Approval")
                body += "--\n"
                hg.mail_create(self, email_from, employee.work_email, subject, body)
        return self.write({'state': 'approve','hr_manager_id': self.env.uid, 'hr_manager_date': fields.date.today()})

    # @api.multi
    # def action_approve_gm(self):
    #     employee = self.employee_id.sudo()
    #     parent = employee.parent_id.sudo()
    #     email_from = hg.get_email_from(self)
    #     if email_from:
    #         if ((employee) and parent) and parent.work_email:
    #             subject = ("Leave request was approved for employee : '%s' ") % (employee.name)
    #             body = _("Hello,\n\n")
    #             body += _("Leave request was approved for employee : '%s' by GM Manager") % (employee.name)
    #             body += "--\n"
    #             hg.mail_create(self, email_from, parent.work_email, subject, body)
    #
    #         if (employee) and employee.work_email:
    #             subject = ("Your leave request was approved")
    #             body = _("Hello,\n\n")
    #             body += _("Your leave request was approved by HR Manager . Happy Journey")
    #             body += "--\n"
    #             hg.mail_create(self, email_from, employee.work_email, subject, body)
    #
    #     return self.write({'state': 'gm_approve', 'gm_manager_id': self.env.uid, 'gm_manager_date': fields.date.today()})




class hr_holidays_deduction_summary_saudi(models.Model):
    _name = 'hr.holidays.deduction.summary.saudi'

    leave_id = fields.Many2one('hr.leave', string='Leave', required=True, readonly=True)
    deduction_type = fields.Selection(related='leave_id.leave_type_id.deduction_type', required=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True)
    date = fields.Datetime(string='Date', required=True, readonly=True, )
    amount = fields.Float(string='Amount', required=True, readonly=True)

    state = fields.Selection([
            ('deducted', 'Deducted'),
            ('undeducted', 'Undeducted'),
            ],
            'Status', readonly=True, track_visibility='onchange', default='undeducted')







     
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
