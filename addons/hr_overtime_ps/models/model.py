# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
from datetime import datetime,timedelta
import math



class hr_overtime_ps(models.Model):
    _name = 'hr.overtime.ps'
    _inherit = ['mail.thread', 'resource.mixin']

    @api.model
    def _get_employee(self):
        result = False
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if employee_ids:
            result = employee_ids[0]
        return result

    @api.one
    @api.depends('employee_id')
    def _get_employee_details(self):
        self.department_id = self.employee_id.department_id.id or False
        self.job_id = self.employee_id.job_id.id or False

    @api.one
    def _get_current_user(self):
        self.current_user = False
        if (self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id.user_id) and self.employee_id.parent_id.user_id.id == self.env.uid:
            self.current_user = True

    @api.one
    @api.depends('overtime_summary.request_hours','overtime_summary.approved_hours')
    def _compute_hours(self):
        self.request_hours = sum(line.request_hours for line in self.overtime_summary) or 0.00
        self.approved_hours = sum(line.approved_hours for line in self.overtime_summary) or 0.00

    @api.one
    @api.depends('employee_id')
    def _get_employee_details(self):
        self.department_id = self.employee_id.department_id.id or False
        self.job_id = self.employee_id.job_id.id or False

    name = fields.Char(string='Serial', default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=False, states={'approve': [('readonly', True)],'refuse': [('readonly', True)],}, default=_get_employee)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True, readonly=False, states={'approve': [('readonly', True)],'refuse': [('readonly', True)],})

    department_id = fields.Many2one('hr.department', string='Department', store=True, readonly=True, compute='_get_employee_details')
    job_id = fields.Many2one('hr.job', string='Job', store=True, readonly=True, compute='_get_employee_details')
    date_from = fields.Date(string='Start Date', required=True, readonly=False, states={'approve': [('readonly', True)],'refuse': [('readonly', True)],},)
    date_to = fields.Date(string='End Date', required=True, readonly=False, states={'approve': [('readonly', True)],'refuse': [('readonly', True)],},)
    overtime_summary = fields.One2many('hr.overtime.summary.ps', 'overtime_id', string='OverTime Summary', readonly=False, states={'approve': [('readonly', True)],'refuse': [('readonly', True)],})
    request_hours = fields.Float(string='Request Hours', digits=dp.get_precision('Account'),store=True, readonly=True, compute='_compute_hours')
    approved_hours = fields.Float(string='Approved Hours', digits=dp.get_precision('Account'),store=True, readonly=True, compute='_compute_hours')
    current_user = fields.Boolean(string='Current User', readonly=True, compute='_get_current_user')
    confirmed_by = fields.Many2one('res.users', string='Confirmed By', readonly=True,)
    confirmed_date = fields.Datetime(string='Confirmed Date', readonly=True,)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True,)
    approved_date = fields.Datetime(string='Approved Date', readonly=True,)
    refused_by = fields.Many2one('res.users', string='Refused By', readonly=True,)
    refused_date = fields.Datetime(string='Refused Date', readonly=True,)

    ot_per_hour = fields.Float(string='OT Per Hour Amount', default=1.5, readonly=False, states={'approve': [('readonly', True)],'refuse': [('readonly', True)],},)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=False, states={'approve': [('readonly', True)],'refuse': [('readonly', True)],},
        default=lambda self: self.env['res.company']._company_default_get('hr.holidays.saudi'))
    note = fields.Html(string='Note', )
    state = fields.Selection([
            ('draft', 'Draft'),
            ('request', 'Waiting for Confirm'),
            ('confirm', 'Waiting for Approval'),
            ('approve', 'Approved'),
            ('refuse', 'Refused'),
            ],
            'Status', readonly=True, track_visibility='onchange', default='draft')

    @api.constrains('date_from','date_to')
    def _date_check(self):
        if self.date_from > self.date_to:
            raise except_orm(_('Invalid Date!'), _('The Date From should be less than or equal Date To'))

    @api.model
    def create(self, values):
        if values.get('name', 'New') == 'New':
            values['name'] = self.env['ir.sequence'].next_by_code('hr.overtime.ps') or 'New'
        result = super(hr_overtime_ps, self).create(values)
        return result

    @api.multi
    def onchange_employee_id(self, employee_id):
        contract = False
        if not employee_id:
            return {'value': {'contract_id': False}}
        contract_ids = self.env['hr.contract'].search([('employee_id', '=', employee_id)])
#        raise except_orm(_('Configuration Error!'), _(contract_ids))
        if contract_ids:
            for record in contract_ids:
                contract = self.env['hr.contract'].browse(record.id).id
        return {'value': {'contract_id': contract}}

    @api.multi
    def on_change_date_from_to(self, date_from, date_to):
        if (date_from and date_to) and date_from > date_to:
            raise except_orm(_('Invalid Date!'), _('The Date From should be less than or equal Date To'))

    @api.multi
    def action_request(self):
        if not self.overtime_summary:
            raise Warning(_('You cannot send request without work summary.'))
        return self.write({'state': 'request'})

    @api.multi
    def action_confirm(self):
        return self.write({'state': 'confirm','confirmed_by': self.env.uid, 'confirmed_date': fields.date.today() })

    @api.multi
    def action_approve(self):
        return self.write({'state': 'approve','approved_by': self.env.uid, 'approved_date': fields.date.today() })

    @api.multi
    def action_refuse(self):
        return self.write({'state': 'refuse','refused_by': self.env.uid, 'refused_date': fields.date.today() })

    @api.multi
    def unlink(self):
        if self.state not in ('draft'):
            raise Warning(_('You cannot delete an OverTime which is not draft.'))
        return super(hr_overtime_ps, self).unlink()

class hr_overtime_summary_ps(models.Model):
    _name = 'hr.overtime.summary.ps'
    _inherit = ['mail.thread', 'resource.mixin']

    overtime_id = fields.Many2one('hr.overtime.ps', string='OverTime', required=True, ondelete='cascade', select=True,)
    name = fields.Char(string='Description', required=True, translate=True)
    date = fields.Date(string='Date', required=True,)
    request_hours = fields.Float(string='Request Hours', required=True,)
    approved_hours = fields.Float(string='Approved Hours',)

    state = fields.Selection([('draft', 'Draft'),], 'Status', readonly=True, track_visibility='onchange', default='draft')

    @api.constrains('date')
    def _date_check(self):
        if self.date < self.overtime_id.date_from or self.date > self.overtime_id.date_to:
            raise except_orm(_('Invalid Date!'), _('The Date should in the range of Date From and Date To'))

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def overtime_compute(self, employee, date_from, date_to, wage, deduction_type):
        approved_hours = total = 0
        overtime_ids = self.env['hr.overtime.ps'].search([('employee_id','=', employee), ('date_from','>=', date_from), ('date_to','>=', date_from), ('state','=', 'approve')])
        for record in overtime_ids:approved_hours += record.approved_hours
        total = approved_hours * ((wage / 30) / 8)
        return total


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
