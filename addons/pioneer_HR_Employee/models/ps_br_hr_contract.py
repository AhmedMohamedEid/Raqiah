from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import except_orm, Warning, RedirectWarning
from lxml import etree
import math



class hr_contract(models.Model):
    _inherit = "hr.contract"

    @api.multi
    @api.depends('employee_id')
    def _no_kids(self):
        for case in self:
            no_kids = 0
            if case.employee_id:
                emp_family_ids = case.employee_id.family_ids
                if emp_family_ids:
                    for emp_family in emp_family_ids:
                        if emp_family.relation_type == 'son' or emp_family.relation_type == 'daughter':
                            no_kids = no_kids + 1
            case.no_kids = no_kids

    @api.multi
    @api.depends('employee_id','gosi_applicable','wage','housing','employee_id.country_id.code')
    def _gosi(self):
        for r in self:
            gosi = 0
            if r.employee_id:
                if r.employee_id.country_id.code == 'SA':
                    if r.gosi_applicable:
                        gosi = (r.wage + r.housing) / 10
            r.gosi = gosi

    @api.multi
    @api.depends('employee_id','wage','housing','food'
                    ,'transportation','mobile','tuition'
                    ,'work','ticket_allowance','living_cost'
                    ,'other')
    def _gross(self):
        result = {}
        for r in self:
            gross = 0
            if r.employee_id:
                gross = r.wage + r.housing + r.food \
                        + r.transportation + r.mobile \
                        + r.tuition + r.work \
                        + r.ticket_allowance + r.living_cost + r.other
            r.gross = gross

    @api.multi
    @api.depends('employee_id','wage','housing','food'
                    ,'transportation','mobile','tuition'
                    ,'work','ticket_allowance','living_cost'
                    ,'other','hrdf','sale','gosi','medical_expense'
        ,'work_permits_expense','iqama_expense','exit_reentry_expense')
    def _net(self):
        for r in self:
            net = 0
            if r.employee_id:
                deduct = r.hrdf + r.sale + r.gosi
                         # + r.medical_expense + r.work_permits_expense \
                         # + r.iqama_expense + r.exit_reentry_expense
                net = r.gross - deduct
            r.net = net
    @api.multi
    def get_availed_leaves(self):
        for case in self:
            case.availed_leaves = 0

    @api.multi
    def get_absent_leaves(self):
        for case in self:
            case.absent_leaves = 0

    @api.multi
    def get_consumed_company_tickets(self):
        for case in self:
            case.consumed_company_tickets = 0

    employee_name = fields.Char(related='employee_id.name', string='Employee Name')
    housing = fields.Float('Housing', help="Specify if the Housing.")
    transportation = fields.Float('Transportation', help="Specify if the Transportation.")
    mobile = fields.Float('Mobile', help="Specify if the Mobile.")
    living_cost = fields.Float('Living Cost')
    other = fields.Float('Other', help="Specify if the Other.")
    annual_leave_period = fields.Float(string='Annual Period(In Days)')
    ticket_allowance = fields.Float('Ticket Allowance')
    medical_expense = fields.Float('Medical Expense')
    no_ticekts_allowed_per_year = fields.Integer(string='Number of Tickets Allowed Per Year')
    consumed_company_tickets = fields.Integer('Company Tickets Consumed', compute='get_consumed_company_tickets')
    annual_leave_type = fields.Selection([('paid','Paid'),('unpaid','Un-Paid')], string='Annual Leave')
    gosi = fields.Float(compute='_gosi', string='Gosi', store=True)
    gosi_applicable = fields.Boolean('Gosi Applicable', default=True)
    availed_leaves = fields.Float('Leave', compute='get_availed_leaves')
    absent_leaves = fields.Float('Absent', compute='get_absent_leaves')

    hrdf = fields.Float('HRDF', help="Specify if the HRDF Salary.")
    sale = fields.Float('Sale', help="Specify if the Sale Salary.")
    food = fields.Float('Food', help="Specify if the Food.")
    tuition = fields.Float('Tuition', help="Specify if the Tuition.")
    work = fields.Float('Duty Allowance', help="Specify if the Duty Allowance.")
    major = fields.Float('Major', help="Specify if the Major.")
    education = fields.Float('Education', help="Specify if the Education.")
    emp_med = fields.Selection(
        [('na', 'N/A'), ('a', 'Class A'), ('b', 'Class B'), ('c', 'Class C'), ('vip', 'VIP')],
        'Employee Medical Class', track_visibility='onchange', help='Choose Employee Medical Class.')
    wife_med = fields.Selection(
        [('na', 'N/A'), ('a', 'Class A'), ('b', 'Class B'), ('c', 'Class C'), ('vip', 'VIP')], 'Wife Medical Class',
        track_visibility='onchange', help='Choose Wife Medical Class.')
    kids_med = fields.Selection(
        [('na', 'N/A'), ('a', 'Class A'), ('b', 'Class B'), ('c', 'Class C'), ('vip', 'VIP')], 'Kids Medical Class',
        track_visibility='onchange', help='Choose Kids Medical Class.')
    no_kids = fields.Integer(compute='_no_kids', string='No of Kids')
    pregnent = fields.Boolean('Pregnant', help="Specify if the Pregnant.")
    gross = fields.Float(compute='_gross', string='Gross', )
    net = fields.Float(compute='_net', string='Net', )
    sponsor_company_id = fields.Many2one('res.company', string='Sponsor', default=lambda self: self.env.user.company_id)
    payroll_company_id = fields.Many2one('res.company', 'Payroll Company',
                                         default=lambda self: self.env.user.company_id)
    work_permits_expense = fields.Float('Work Permits Expense')
    iqama_expense = fields.Float('Iqama Expense')
    exit_reentry_expense = fields.Float('Exit / Re-entry Expense')

    @api.onchange('employee_id')
    @api.multi
    def onchange_employee_id(self):
        for case in self:
            employee = case.employee_id
            case.job_id = employee.job_id and employee.job_id.id or False
            case.employee_name = employee.name or ''
            # case.sponsor_company_id = employee.sponsor_company_id and employee.sponsor_company_id.id or False
            # case.payroll_company_id = employee.company_id and employee.company_id.id or False
            # TODO move this function into hr_contract module, on hr.employee object

    # @api.model
    # def create(self,vals):
    #     type_id = vals['type_id']
    #     cr = self._cr
    #     if type_id:
    #         con_type = self.env['hr.contract.type'].browse(type_id)
    #         contract_type = con_type.contract_type
    #         if contract_type == 'employee':
    #             cr.execute("update hr_employee set contract_type = 'employee',contract_date = '%s' where id = %s" % (
    #             vals['date_start'], vals['employee_id']))
    #         elif contract_type == 'worker':
    #             cr.execute("update hr_employee set contract_type = 'worker',contract_date = '%s' where id = %s" % (
    #             vals['date_start'], vals['employee_id']))
    #     return super(hr_contract, self).create(vals)
    #
    # @api.multi
    # def write(self, vals):
    #     for case in self:
    #         cr = self._cr
    #         type_id = vals.get('type_id', case.type_id.id) or False
    #         emp_id = vals.get('employee_id', case.employee_id.id) or False
    #         date_start = vals.get('date_start', case.date_start)
    #         con_type = self.env['hr.contract.type'].browse(type_id)
    #         contract_type = con_type.contract_type
    #         if contract_type:
    #             if emp_id:
    #                 if contract_type == 'employee':
    #                     cr.execute(
    #                         "update hr_employee set contract_type = 'employee',contract_date = '%s' where id = %s" % (
    #                         date_start, emp_id))
    #                 elif contract_type == 'worker':
    #                     cr.execute("update hr_employee set contract_type = 'worker',contract_date = '%s' where id = %s" % (
    #                     date_start, emp_id))
    #     return super(hr_contract, self).write(vals)

