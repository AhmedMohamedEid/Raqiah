# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime, timedelta
from dateutil import relativedelta
import math



class hr_employee_type(models.Model):
    _name = 'hr.employee.type'

    name = fields.Char(string='Name', required=True, translate=True)
    annual_leave_type = fields.Selection([('month', 'Month'), ('year', 'Year'), ], 'Annual Leave Type', required=True,
                                         default='month')
    annual_leave = fields.Float(string='Annual Leave', required=True, digits=dp.get_precision('Decimal Single'))
    leave_carryover_year = fields.Integer(string='Leave Carryover Year', required=True)
    leave_start_month = fields.Integer(string='Leave Start After (month)', required=True)
    leave_start_month_type = fields.Selection([('first_year', 'First Year Only'), ('every_year', 'Every Year'), ],
                                              'Leave Start Type', default='first_year')

    @api.constrains('leave_start_month', 'leave_carryover_year', 'annual_leave')
    def _value_constrains(self):
        if self.annual_leave < 0:
            raise except_orm(_('Invalid Value!'), _('Annual Leave should be possitive'))
        if self.leave_start_month < 0:
            raise except_orm(_('Invalid Value!'), _('Leave Start After (month) should be possitive'))
        if self.leave_carryover_year < 0:
            raise except_orm(_('Invalid Value!'), _('Leave Carryover Year should be possitive'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
