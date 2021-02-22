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








     
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
