# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import except_orm, Warning, RedirectWarning
import dateutil
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class eosb_eosb(models.Model):
    _name = 'eosb.eosb'
    _inherit = ['mail.thread', 'resource.mixin']

    @api.one
    @api.depends('date')
    def _compute_worked_duration(self):
        self.no_days = 0
        self.no_months = 0
        self.no_years = 0
        if self.date and self.joined_date:
            start_date = self.joined_date
            end_date = self.date + timedelta(days=1)
            self.worked_days = (end_date - start_date).days
            self.worked_months = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)
            self.worked_years = relativedelta(end_date, start_date).years
            self.no_days = relativedelta(end_date, start_date).days + 1
            self.no_months = relativedelta(end_date, start_date).months
            self.no_years = relativedelta(end_date, start_date).years
            self.worked_period = str(self.no_years) + ' Years: ' + str(self.no_months) + ' Months: ' + str(
                self.no_days) + ' Days'
        return

    @api.one
    @api.depends('payslip_line_ids', 'payslip_line_ids.amount', 'eosb_based', 'salary_rules_ids', 'rules_ids',
                 'employee_id', 'contract_id')
    def _compute_salary(self):
        amount = 0
        if self.eosb_based in ('custom', 'net'):
            amount = sum(line.total for line in self.payslip_line_ids if line.salary_rule_id.category_id.code == 'NET')
        elif self.eosb_based == 'wage':
            amount = self.contract_id.wage
        self.salary = amount

    @api.model
    def _rule_domain(self):
        rule_domain = []
        rule_ids = self.env['hr.salary.rule'].search([])
        rule_domain += [rule.id for rule in rule_ids if rule.category_id.code not in ('BASIC', 'GROSS', 'NET')]
        return [('id', 'in', rule_domain)]

    def _get_default_struct_rule(self, struct_id, rule_domain):
        rule_domain += [rule.id for rule in struct_id.rule_ids if rule.category_id.code in ('BASIC', 'GROSS', 'NET')]
        if struct_id.parent_id: self._get_default_struct_rule(struct_id.parent_id, rule_domain)
        return rule_domain

    @api.one
    @api.depends('rules_ids', 'eosb_based', 'employee_id', 'contract_id')
    def _compute_salary_rules(self):
        self.salary_rules_ids = False
        if self.eosb_based == 'custom':
            rule_domain = []
            #            rule_ids = self.env['hr.salary.rule'].search([])
            rule_domain += self._get_default_struct_rule(self.contract_id.struct_id, rule_domain)
            rule_domain += [rule.id for rule in self.rules_ids]
            self.salary_rules_ids = [(6, 0, [x for x in rule_domain])]

    def _get_eosb_amount(self):
        result = 0
        if (self.employee_id) and self.eosb_emp_type_id:
            eosb_condition = {}
            if self.eosb_type == 'resignation':
                eosb_condition = self.eosb_emp_type_id.eosb_emp_type_resignation
            elif self.eosb_type == 'termination':
                eosb_condition = self.eosb_emp_type_id.eosb_emp_type_termination
            years = self.no_years
            if self.eosb_emp_type_id.period_consider == 'year_month' and self.no_months > 0:
                years += 1
            elif self.eosb_emp_type_id.period_consider == 'year_month_day' and (self.no_months > 0 or self.no_days > 0):
                years += 1

            value = 0
            value2 = []
            temp_year = 0
            for line in eosb_condition:
                if years > temp_year:
                    if line.calculation_type == 'fixed':
                        value = line.value
                        value2 += [(line.year, temp_year, value)]
                    elif line.calculation_type == 'percentage':
                        value = (self.salary * line.value) / 100
                        value2 += [(line.year, temp_year, value)]
                    elif line.calculation_type == 'fraction':
                        value = self.salary / line.value
                        value2 += [(line.year, temp_year, value)]
                    temp_year = line.year
            if self.eosb_emp_type_id.calculate_based == True:
                result = value * years
                if self.eosb_emp_type_id.calculation_consider == 'even_month':
                    if self.no_months > 0: result = (value * (self.no_years)) + ((value / 12) * self.no_months)
                elif self.eosb_emp_type_id.calculation_consider == 'even_day':
                    if self.no_months > 0: result = (value * (self.no_years)) + ((value / 12) * self.no_months)
                    if self.no_days > 0: result += (((value / 12) / 30) * self.no_days)
                elif self.eosb_emp_type_id.calculation_consider == 'actual_year':
                    result = value * (self.no_years)
            else:
                if len(value2) > 0:
                    for i in value2: result += (i[0] - i[1]) * i[2]
                    result = self.currect_eosb_result(i, years, result)
                    if self.eosb_emp_type_id.calculation_consider == 'even_month':
                        if self.eosb_emp_type_id.period_consider in (
                        'year_month', 'year_month_day') and self.no_months > 0:
                            result -= i[2]
                            result += ((i[2] / 12) * self.no_months)
                    if self.eosb_emp_type_id.calculation_consider == 'even_day':
                        if self.eosb_emp_type_id.period_consider in (
                        'year_month', 'year_month_day') and self.no_months > 0:
                            result -= i[2]
                            result += ((i[2] / 12) * self.no_months)
                        if self.no_days > 0: result += (((i[2] / 12) / 30) * self.no_days)
                    if self.eosb_emp_type_id.calculation_consider == 'actual_year':
                        if self.eosb_emp_type_id.period_consider in (
                        'year_month', 'year_month_day') and self.no_months > 0:
                            result -= i[2]
                        elif self.eosb_emp_type_id.period_consider in ('year_month_day') and self.no_days > 0:
                            result -= i[2]
                    #                    print value2[-2][2]
        return result

    def currect_eosb_result(self, i, years, result):
        if years > i[0]: result += (years - i[0]) * i[2]
        if years < i[0]: result -= (i[0] - years) * i[2]
        return result

    def _get_leave_salary_amount(self):
        result = 0
        if self.provide_leave_salary: result = (self.contract_id.wage / 30) * self.employee_id.balance_leave
        return result

    def _get_gross_amount(self):
        result = self._get_eosb_amount() + self.other_allowance
        if self.provide_leave_salary:
            result += self._get_leave_salary_amount()
        return result

    def _get_deduction_amount(self):
        result = self.other_deduction
        return result

    def _get_net_amount(self):
        result = self._get_gross_amount() - self._get_deduction_amount()
        return result

    @api.one
    @api.depends('salary')
    def _compute_amount(self):
        self.eosb_amount = self._get_eosb_amount()
        self.leave_salary_amount = self._get_leave_salary_amount()
        self.gross_amount = self._get_gross_amount()
        self.deduction_amount = self._get_deduction_amount()
        self.net_amount = self._get_net_amount()

    def _get_currency(self):
        user = self.env['res.users'].browse([self.env.uid])[0]
        return user.company_id.currency_id

    @api.multi
    def get_employee_details(self):
        for case in self:
            employee = case.employee_id.sudo()
            case.job_id = employee.job_id.id
            case.department_id = employee.department_id.id
            case.eosb_emp_type_id = employee.eosb_emp_type_id.id
            try:
                case.joined_date = employee.joined_date
            except:
                case.joined_date = False#employee.joined_date
            try:
                case.type_id = employee.type_id.id
            except:
                case.type_id = False#employee.joined_date
            try:
                case.availed_leave = employee.availed_leave
            except:
                case.availed_leave = 0#employee.joined_date
            try:
                case.used_leave = employee.used_leave
            except:
                case.used_leave = 0  # employee.joined_date
            try:
                case.balance_leave = employee.balance_leave
            except:
                case.balance_leave = 0  # employee.joined_date

    name = fields.Char(string='Serial')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=False,
                                 )
    job_id = fields.Many2one('hr.job', string="Job", readonly=True, compute='get_employee_details')
    department_id = fields.Many2one('hr.department', string="Department", readonly=True, compute='get_employee_details')
    joined_date = fields.Datetime(string='Date of Joined', readonly=True, compute='get_employee_details')
    eosb_emp_type_id = fields.Many2one('eosb.emp.type', string="EOSB Category", readonly=True,
                                       compute='get_employee_details')
    eosb_type = fields.Selection([('resignation', 'Resignation'), ('termination', 'Termination')], string='Type',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})
    contract_id = fields.Many2one('hr.contract', string="Contract", required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    eosb_based = fields.Selection([('wage', 'By Wage'), ('net', 'By Net'), ('custom', 'By Custom')],
                                  string='EOSB Based', default='wage', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    payslip_id = fields.Many2one('hr.payslip', string="Payslip", readonly=True, states={'draft': [('readonly', False)]})
    payslip_line_ids = fields.One2many(related='payslip_id.line_ids', string="Payslip Lines", readonly=True,
                                       states={'draft': [('readonly', False)]})
    salary = fields.Float(string="Salary", required=True, compute='_compute_salary')
    rules_ids = fields.Many2many('hr.salary.rule', string="Payslip Rule", domain=_rule_domain, readonly=True,
                                 states={'draft': [('readonly', False)]})
    salary_rules_ids = fields.Many2many('hr.salary.rule', string="Base Payslip Rule", compute='_compute_salary_rules')
    current_month_payslip_id = fields.Many2one('hr.payslip', string="Current Month Payslip", readonly=True,
                                               states={'draft': [('readonly', False)]})
    current_month_payslip_line_ids = fields.One2many(related='current_month_payslip_id.line_ids',
                                                     string="Current Month Payslip Lines")
    gen_cur_payslip = fields.Boolean(string='Generate Current month Payslip', readonly=True,
                                     states={'draft': [('readonly', False)]})
    date = fields.Date(string='Last Worked Date', required=True, default=lambda self: fields.date.today(),
                       readonly=True, states={'draft': [('readonly', False)]})
    payslip_days = fields.Integer(string='Days', help="Specify if want generate payslip for corresponding days",
                                  readonly=True, states={'draft': [('readonly', False)]})
    other_allowance = fields.Float(string='Other Allowance', readonly=True, states={'draft': [('readonly', False)]})
    other_deduction = fields.Float(string='Other Deduction', readonly=True, states={'draft': [('readonly', False)]})
    eosb_amount = fields.Float(string='EOSB Amount', compute='_compute_amount')
    gross_amount = fields.Float(string='Gross Amount', compute='_compute_amount')
    deduction_amount = fields.Float(string='Total Deduction Amount', compute='_compute_amount')
    net_amount = fields.Float(string='Net Amount', compute='_compute_amount')
    provide_leave_salary = fields.Boolean(string='Provide Balance Leave Salary', readonly=True,
                                          states={'draft': [('readonly', False)]})
    leave_salary_amount = fields.Float(string='Leave Salary Amount', compute='_compute_amount')
    no_days = fields.Integer(string='No of Days Worked', compute='_compute_worked_duration')
    no_months = fields.Integer(string='No of Months Worked', compute='_compute_worked_duration')
    no_years = fields.Integer(string='No of Years Worked', compute='_compute_worked_duration')

    worked_days = fields.Integer(string='No of Days Worked', compute='_compute_worked_duration')
    worked_months = fields.Integer(string='No of Months Worked', compute='_compute_worked_duration')
    worked_years = fields.Integer(string='No of Years Worked', compute='_compute_worked_duration')
    worked_period = fields.Char(string='Worked Period', compute='_compute_worked_duration')

    leave_type_id = fields.Many2one('hr.holidays.type.saudi', string='Leave Type', readonly=True,
                                    compute='get_employee_details')
    availed_leave = fields.Float(string='Availed Leave', readonly=True, compute='get_employee_details')
    used_leave = fields.Float(string='Used Leave', readonly=True, compute='get_employee_details')
    balance_leave = fields.Float(string='Balance Leave', readonly=True, compute='get_employee_details')

    move_id = fields.Many2one('account.move', string="Journal Entry", readonly=True,
                              states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string="Force Journal", readonly=True,
                                 states={'confirm': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=_get_currency,
                                  readonly=True, states={'draft': [('readonly', False)]})

    note = fields.Text(string='Remarks', readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('eosb.eosb'),
                                 readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('validate', 'Validate'),
        ('refuse', 'Refused'),
    ], string='Status', readonly=True, track_visibility='onchange', default='draft')

    _sql_constraints = [
        ('employee_id_uniq', 'unique(employee_id,eosb_type)', 'You cannot create EOSB more than once for each Employee!')]

    @api.constrains('employee_id')
    def _employee_constrains(self):
        if (self.employee_id) and (
        not self.employee_id.address_home_id) and not self.employee_id.address_home_id.property_account_payable_id:
            raise Warning(
                _('The employee must be have a Home Address and Home Address must be have a Account Payable.'))

    @api.constrains('payslip_days')
    def _payslip_days_constrains(self):
        if self.gen_cur_payslip and self.payslip_days >= 0:
            month = self.date.month
            monthdays = [(1, 31), (2, 29), (3, 31), (4, 30), (5, 31), (6, 30), (7, 31), (8, 31), (9, 30), (10, 31),
                         (11, 30), (12, 31)]
            day = [val for id, val in monthdays if id == month]
            if self.payslip_days > day[0]:
                raise Warning(_('Invalid Days'))

    @api.model
    def create(self, values):
        print ('values',values)
        if values.get('name', 'New') == 'New':
            values['name'] = self.env['ir.sequence'].next_by_code('eosb.eosb') or 'New'
        result = super(eosb_eosb, self).create(values)
        return result

    @api.multi
    def unlink(self):
        if self.state not in ('draft', False):
            raise Warning(_('You cannot delete record which is not in Draft.'))
        return models.Model.unlink(self)

    @api.onchange('employee_id', 'eosb_based')
    def _onchange_employee(self):
        self.rules_ids = False
        self.contract_id = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], limit=1,
                                                          order='date_start desc').id

    @api.multi
    def compute_sheet(self):
        if not self.employee_id.eosb_emp_type_id: raise Warning(_("Please assign 'EOSB Category' for this employee"))
        if self.eosb_based == 'wage': self.payslip_id.unlink()
        if self.eosb_based in ('net', 'custom') and not self.payslip_id:
            vals = {
                'employee_id': self.employee_id.id,
                'date_from': self.date,  # datetime.strptime(self.date, '%Y-%m-%d').strftime('%Y-%m-01'),
                'date_to': self.date,
                # str(datetime.strptime(self.date, '%Y-%m-%d') + relativedelta(months=+1, day=1, days=-1))[:10],
                'contract_id': self.contract_id.id,
                'struct_id': self.contract_id.struct_id.id,
                'name': ('Salary Slip of %s for EOSB') % (self.employee_id.name),
                'eosb': True,
            }
            if self.eosb_based == 'custom':
                vals.update({'eosb_rules_ids': [(6, 0, [x.id for x in self.salary_rules_ids])]})
            payslip_id = self.env['hr.payslip'].create(vals)
            payslip_id.compute_sheet()
            self.payslip_id = payslip_id.id
            payslip_id.write({'state': 'cancel'})
        elif self.eosb_based in ('net', 'custom') and self.payslip_id:
            self.payslip_id.employee_id = self.employee_id.id
            self.payslip_id.date_from = self.date  # datetime.strptime(self.date, '%Y-%m-%d').strftime('%Y-%m-01')
            self.payslip_id.date_to = self.date  # str(datetime.strptime(self.date, '%Y-%m-%d') + relativedelta(months=+1, day=1, days=-1))[:10]
            self.payslip_id.contract_id = self.contract_id.id
            self.payslip_id.struct_id = self.contract_id.struct_id.id
            self.payslip_id.name = ('Salary Slip of %s for EOSB') % (self.employee_id.name)
            self.payslip_id.eosb = True
            self.payslip_id.eosb_rules_ids = self.salary_rules_ids
            self.payslip_id.compute_sheet()

        return True

    @api.multi
    def action_confirm(self):
        self.compute_sheet()
        return self.write({'state': 'confirm'})

    @api.multi
    def action_reset(self):
        self.compute_sheet()
        return self.write({'state': 'draft'})

    @api.multi
    def action_validate(self):
        self.compute_sheet()
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        # nazar_obj = self.env['account.nazar']
        company_currency = self.company_id.currency_id.id
        diff_currency_p = self.currency_id.id != company_currency
        if not self.employee_id.address_home_id: raise Warning(_('Please set the home address for employee'))
        ref = self.employee_id.name + '/' + 'EOSB'
        # config = self.env['hr.accounting.config']._get_hr_accounting_config()
        journal_id = self.journal_id
        company_id = self.company_id
        if not journal_id:
            #            raise Warning(_(config_id))
            if company_id.eosb_eosb_journal_id:
                journal_id = company_id.eosb_eosb_journal_id
        if not journal_id:
            msg = 'Set a journal in company - ' + str(company_id.name) + ' or set a force journal.'
            raise UserError(_(msg))
        # move_id = move_obj.create(nazar_obj.account_move_get(self, journal_id, date=fields.datetime.today(), ref=ref, company_id=self.company_id.id))

        vals = {
            'journal_id': journal_id.id,
            'date': fields.datetime.today(),
            # 'period_id': period_obj.find(date)[0],
            'ref': '',
            'company_id': self.company_id.id,
        }

        line1 = [(0, 0, {
            # 'move_id':move_id.id,
            'journal_id': journal_id.id,
            'partner_id': self.employee_id.address_home_id.id,
            'credit': 0,
            'debit': self.net_amount,
            'centralisation': 'normal',
            'company_id': self.company_id.id,
            'state': 'valid',
            'blocked': False,
            'account_id': journal_id.default_debit_account_id.id,
            # 'period_id':move_id.period_id.id,
            'name': 'Loan',
            'amount_currency': diff_currency_p and self.currency_id.id or False,
            'quantity': 1,

        })]
        line1.append((0, 0, {
            # 'move_id':move_id.id,
            'journal_id': journal_id.id,
            'partner_id': self.employee_id.address_home_id.id,
            'credit': self.net_amount,
            'debit': 0,
            'centralisation': 'normal',
            'company_id': self.company_id.id,
            'state': 'valid',
            'blocked': False,
            'account_id': self.employee_id.address_home_id.property_account_payable_id.id,
            # 'period_id':move_id.period_id.id,
            'name': '/',
            'amount_currency': diff_currency_p and self.currency_id.id or False,
            'quantity': 1,

        }))
        vals.update({'line_ids': line1})

        move_id = move_obj.create(vals)

        if self.gen_cur_payslip and not self.current_month_payslip_id:
            vals = {
                'employee_id': self.employee_id.id,
                'date_from': self.date,  # datetime.strptime(self.date, '%Y-%m-%d').strftime('%Y-%m-01'),
                'date_to': self.date,
                # str(datetime.strptime(self.date, '%Y-%m-%d') + relativedelta(months=+1, day=1, days=-1))[:10],
                'contract_id': self.contract_id.id,
                'struct_id': self.contract_id.struct_id.id,
                'name': ('Salary Slip of %s') % (self.employee_id.name),
                'eosb_days': self.payslip_days,
            }

            current_month_payslip_id = self.env['hr.payslip'].create(vals)
            current_month_payslip_id.compute_sheet()
            self.current_month_payslip_id = current_month_payslip_id
        elif self.gen_cur_payslip and self.current_month_payslip_id:
            self.current_month_payslip_id.compute_sheet()
        return self.write({'state': 'validate', 'move_id': move_id.id})

    @api.multi
    def action_refuse(self):
        return self.write({'state': 'refuse'})


class eosb_emp_type(models.Model):
    _name = 'eosb.emp.type'

    @api.one
    @api.depends('calculate_based')
    def _get_info(self):
        if self.calculate_based:
            self.calculate_info = 'Calculation Example:\nEmployee Total Worked Years = 10\n2 Years = 1000\n5 Years = 1500\n10 Years = 2000\nCalculated Amount: 2000 * 10 = 20000'
        else:
            self.calculate_info = 'Calculation Example:\nEmployee Total Worked Years = 10\n2 Years = 1000\n5 Years = 1500\n10 Years = 2000\nCalculated Amount: (1000 * 2) + (1500 * 3) + (2000 * 5) = 16500'


        #    name = fields.Char(string='Name', required=True, readonly=True, states={'draft': [('readonly', False)]})
        #    eosb_emp_type_resignation = fields.One2many('eosb.emp.type.resignation', 'eosb_emp_type_resignation_id', string='Employee Resignation Type', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
        #    eosb_emp_type_termination = fields.One2many('eosb.emp.type.termination', 'eosb_emp_type_termination_id', string='Employee Termination Type', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
        #    calculate_based = fields.Boolean(string='Calculation Consider By Bulk of Year', default=False, readonly=True, states={'draft': [('readonly', False)]})
        #    calculate_info = fields.Text(string='Info', compute='_get_info')
        #    period_consider = fields.Selection([('year_only','Years Only'),('year_month','Even Months'),('year_month_day','Even Days')], string='Period Consider for Case Selection', required=True, default='year_only', readonly=True, states={'draft': [('readonly', False)]})
        #    calculation_consider = fields.Selection([('period_year','Period Consider Year'),('actual_year','Actual Year'),('even_month','Even Months'),('even_day','Even Days')], string='Calculation Consider', required=True, default='period_year', readonly=True, states={'draft': [('readonly', False)]})

    name = fields.Char(string='Name', required=True)
    eosb_emp_type_resignation = fields.One2many('eosb.emp.type.resignation', 'eosb_emp_type_resignation_id',
                                                string='Employee Resignation Type', copy=True)
    eosb_emp_type_termination = fields.One2many('eosb.emp.type.termination', 'eosb_emp_type_termination_id',
                                                string='Employee Termination Type', copy=True)
    calculate_based = fields.Boolean(string='Calculation Consider By Bulk of Year', default=False, )
    calculate_info = fields.Text(string='Info', compute='_get_info')
    period_consider = fields.Selection(
        [('year_only', 'Years Only'), ('year_month', 'Even Months'), ('year_month_day', 'Even Days')],
        string='Period Consider for Case Selection', required=True, default='year_only')
    calculation_consider = fields.Selection(
        [('period_year', 'Period Consider Year'), ('actual_year', 'Actual Year'), ('even_month', 'Even Months'),
         ('even_day', 'Even Days')], string='Calculation Consider', required=True, default='period_year')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ],
        'Status', readonly=True, track_visibility='onchange', default='draft')

    @api.multi
    def validate_lines(self, records, categ):
        temp = 0
        for line in records:
            if categ == 'resignation':
                msg = 'Resignation Year should be ascending'
            else:
                msg = 'Termination Year should be ascending'
            if temp != 0 and temp >= line.year: raise except_orm(_('Invalid Value !'), _(msg))
            temp = line.year
        return True

    @api.multi
    def action_active(self):
        self.validate_lines(self.eosb_emp_type_resignation, 'resignation')
        self.validate_lines(self.eosb_emp_type_termination, 'termination')
        return self.write({'state': 'active'})

    @api.multi
    def action_inactive(self):
        return self.write({'state': 'inactive'})

    @api.multi
    def action_reactive(self):
        return self.write({'state': 'active'})

    @api.multi
    def unlink(self):
        self.ensure_one()
        if self.state not in ('draft', False):
            raise Warning(_('You cannot delete record which is not in Draft.'))
        return models.Model.unlink(self)


class eosb_emp_type_resignation(models.Model):
    _name = 'eosb.emp.type.resignation'

    eosb_emp_type_resignation_id = fields.Many2one('eosb.emp.type', string='EOSB Category', ondelete='cascade',
                                                   index=True, copy=False)
    year = fields.Integer(string='Year', required=True)
    calculation_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage'), ('fraction', 'Fraction')],
                                        string='Calculation Type', required=True)
    value = fields.Float(string='Value', required=True)

    @api.constrains('value')
    def _value_constrains(self):
        if self.calculation_type == 'percentage' and self.value > 100:
            raise Warning(_('Percentage value should be less than or equal 100'))


class eosb_emp_type_termination(models.Model):
    _name = 'eosb.emp.type.termination'

    eosb_emp_type_termination_id = fields.Many2one('eosb.emp.type', string='EOSB Category', ondelete='cascade',
                                                   index=True, copy=False)
    year = fields.Integer(string='Year', required=True)
    calculation_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage'), ('fraction', 'Fraction')],
                                        string='Calculation Type', required=True)
    value = fields.Float(string='Value', required=True)

    @api.constrains('value')
    def _value_constrains(self):
        if self.calculation_type == 'percentage' and self.value > 100:
            raise Warning(_('Percentage value should be less than or equal 100'))

# @api.model
#    def create(self, values):
#        raise Warning(_(record_ids))
#        return super(eosb_eosb_type_line, self).create(values)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
