# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime, timedelta
from dateutil import relativedelta
import math


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    def _compute_date(self, date_from, date_to, DATETIME_FORMAT):
        days = months = years = 0
        differents = relativedelta.relativedelta(date_to,
                                                 date_from)
        years = differents.years
        months = (years * 12) + differents.months
        #        days = differents.days
        timedelta = date_to - date_from
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        days = round(math.floor(diff_day))
        return days, months, years

    #    def _compute_year_result(self, employee_id, days, months, years, carryover_month):
    #        result = 0
    #        if carryover_month > 0:
    #            mod = months % carryover_month
    #            if mod <> 0:
    #                a = mod / 12.0
    #                result = int(a) * annual_leave
    #                if a > int(a):
    #                    result += annual_leave
    #            else:
    #                result = employee_id.type_id.leave_carryover_year * annual_leave

    #        else:
    #            result = years * annual_leave
    #            if days > 0:
    #                result += annual_leave
    #        return result

    def _compute_year_result(self, employee_id, days, months, years, carryover_month):
        result = 0
        annual_leave = employee_id.type_id.annual_leave
        if carryover_month > 0:
            diva, moda = divmod(months, carryover_month)
            if moda != 0:
                divb, modb = divmod(moda, 12)
                result = divb * annual_leave
                if modb > 0: result += annual_leave
            else:
                result = employee_id.type_id.leave_carryover_year * annual_leave
        else:
            result = years * annual_leave
            if days > 0:
                result += annual_leave

        check_type = months % 12
        if employee_id.type_id.leave_start_month_type == 'every_year' \
                and employee_id.type_id.leave_start_month > 0 and \
                (check_type < employee_id.type_id.leave_start_month
                        or check_type == employee_id.type_id.leave_start_month and days <= 0):
            result -= annual_leave
        return result

    def _compute_month_result(self, employee_id, days, months, years, carryover_month):
        #775 25 2 12
        print ('carryover_month', carryover_month)
        result = 0
        annual_leave = employee_id.type_id.annual_leave #2.5
        if carryover_month > 0:
            diva, moda = divmod(months, carryover_month)#25,12
            # print('diva, moda', diva, moda)#2,1
            if moda != 0:
                # print ('moda', moda , annual_leave)# 1, 2.5
                result += moda * annual_leave # 2.5
            else:
                # print ('lcy_al_days', employee_id.type_id.leave_carryover_year , annual_leave)
                lcy_al_days = employee_id.type_id.leave_carryover_year * annual_leave * 12
                result += lcy_al_days
        else:
            result += months * annual_leave
            if days > 0: result += annual_leave
        divb, modb = divmod(months, 12)
        if employee_id.type_id.leave_start_month_type == 'every_year' and employee_id.type_id.leave_start_month > 0 and (
                modb < employee_id.type_id.leave_start_month or modb == employee_id.type_id.leave_start_month and days <= 0):
            result -= annual_leave * 12

        return result

    def _compute_leave(self, employee_id):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        days = months = years = result = mod = a = 0
        annual_leave_type = employee_id.type_id.annual_leave_type # Month
        leave_start_month = employee_id.type_id.leave_start_month
        current_date = (datetime.today()).strftime(DATETIME_FORMAT)
        if employee_id.aj_date and employee_id.type_id:
            days, months, years = self._compute_date(employee_id.joined_date, current_date, DATETIME_FORMAT) #2017-01-01
            # print ('days, months, years',days, months, years) # 772 25 2
            if (leave_start_month < months) or (leave_start_month == months and days > 0):
                carryover_month = employee_id.type_id.leave_carryover_year * 12 # 12
                if annual_leave_type == 'year':
                    result += self._compute_year_result(employee_id, days, months, years, carryover_month)
                if annual_leave_type == 'month':
                    result += self._compute_month_result(employee_id, days, months, years, carryover_month)
        return result

    @api.one
    @api.depends('aj_date', 'type_id')
    def _compute_availed_leave(self):
        self.availed_leave = self._compute_leave(self)

    @api.one
    @api.depends('availed_leave', 'used_leave')
    def _compute_balance_leave(self):
        self.balance_leave = self.accumlate_days - self.used_leave

    @api.multi
    def _yearly_vacation_days(self):
        result = {}
        for r in self:
            leave_earn, yearly_leave = self._get_leave_data(r.aj_date, r.contract_date, r.contract_type, r.basic_contract_type)
            if yearly_leave:
                result[r.id] = yearly_leave
            else:
                result[r.id] = yearly_leave
        return result

    @api.one
    def _compute_holidays_count(self):
        self.holidays_count = self.env['hr.leave'].search_count([('employee_id', '=', self.id)])

    @api.multi
    def _compute_accumlate_days(self):
        for r in self:
            leave_earn, yearly_leave = self._get_leave_data(r.aj_date, r.contract_date, r.contract_type, r.basic_contract_type)
            r.accumlate_days = leave_earn

    #inheirted
    aj_date = fields.Date(string='Date of Joined')

    type_id = fields.Many2one('hr.employee.type', string="Type")
    accumlate_days = fields.Float(string='Accumulated Leave', readonly=True, compute='_compute_accumlate_days',
                                  digits=dp.get_precision('Decimal Single'))
    availed_leave = fields.Float(string='Availed Leave', readonly=True, compute='_compute_availed_leave',
                                 digits=dp.get_precision('Decimal Single'))
    used_leave = fields.Float(string='Used Leave', readonly=True,
                              digits=dp.get_precision('Decimal Single'))
    balance_leave = fields.Float(string='Balance Leave', readonly=True, compute='_compute_balance_leave',
                                 digits=dp.get_precision('Decimal Single'))
    holidays_count = fields.Integer(string='Leaves', readonly=True, compute='_compute_holidays_count')
    contract_type = fields.Selection([('employee', 'Employee'), ('worker', 'Worker')], 'Basic Contract Type', default="employee")
    basic_contract_type = fields.Selection([('employee', 'Employee'), ('worker', 'Worker')], 'Basic Contract Type', default="employee")
    last_vacation_date = fields.Date('Last Vacation Date')
    yearly_vacation_days =fields.Char(compute='_yearly_vacation_days',
                                            string='Yearly Vacation Days', ),

    @api.model
    def leave_compute(self, employee, date_from, date_to, deduction_type):
        total = 0
        deduction_ids = self.env['hr.holidays.deduction.summary.saudi'].search(
            [('employee_id', '=', employee), ('date', '>=', date_from), ('date', '<=', date_to),
             ('deduction_type', 'in', deduction_type), ('state', '=', 'undeducted')])
        for record in deduction_ids:
            total += record.amount
        return total

    @api.model
    def overtime_compute(self, employee, date_from, date_to, wage, deduction_type):
        allowance = super(hr_employee, self).overtime_compute(employee, date_from, date_to, wage, deduction_type)
        deduction = self.leave_compute(employee, date_from, date_to, deduction_type)
        total = allowance - deduction
        return total


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
