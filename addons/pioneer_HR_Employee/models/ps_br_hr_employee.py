# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.addons.pioneer_HR_Employee.models import ps_br_hr_config_global as hg

import odoo.addons.decimal_precision as dp
from odoo.exceptions import except_orm, Warning, RedirectWarning
from lxml import etree
from odoo.osv.orm import setup_modifiers

#TO HAVE EASY COPPY
# group_user = self.user_has_groups('base.group_user')
# group_hr_user = self.user_has_groups('hr.group_user')
# group_hr_manager = self.env.user.has_group('hr.group_hr_manager')
# group_hr_general_manager = self.env.user.has_group('pioneer_HR_Employee.group_hr_general_manager')

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _order = 'emp_code_sort'

    #OVERRIDEEN
    def _sync_user(self, user):
        return dict(
            # name=user.name,
            # image=user.image,
            work_email=user.email,
        )

    def action_open_my_page(self):
        print ("called")

        '''
        This function returns an action that display existing delivery orders of given sales order ids. It can either be a in a list or in a form view, if there is only one delivery order to show.
        '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        uid = self._uid
        compose_form_id = mod_obj.get_object_reference('pioneer_HR_Employee', 'custom_view_employee_form_new')[1]


        obj_emp = self.env['hr.employee']
        ids2 = obj_emp.search([('user_id', '=', uid)])
        if not ids2:
            raise UserError(_('The user is not an employee.'))

        #res = mod_obj.get_object_reference(cr, uid, 'hr', 'view_employee_form')
        #result['views'] = [(res and res[1] or False, 'form')]
        result = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id'   : ids2 and ids2.ids[0],
            'res_model': 'hr.employee',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'current',
        }
        return result

    def _compute_leave(self, employee_id):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        days = months = years = result = mod = a = 0
        current_date = (datetime.today()).strftime(DATETIME_FORMAT)
        print('employee_id.aj_date', employee_id.aj_date,employee_id.type_id)
        if employee_id.aj_date and employee_id.type_id:
            days, months, years = self._compute_date(employee_id.aj_date, current_date, DATETIME_FORMAT)
            print ('days, months, years',days, months, years)
            if (employee_id.type_id.leave_start_month < months) or (
                    employee_id.type_id.leave_start_month == months and days > 0):
                carryover_month = employee_id.type_id.leave_carryover_year * 12
                if employee_id.type_id.annual_leave_type == 'year':
                    result += self._compute_year_result(employee_id, days, months, years, carryover_month)
                if employee_id.type_id.annual_leave_type == 'month':
                    result += self._compute_month_result(employee_id, days, months, years, carryover_month)
                    print ('ggg')
        return result

    @api.one
    @api.depends('aj_date', 'type_id')
    def _compute_availed_leave(self):
        self.availed_leave = self._compute_leave(self)

    @api.multi
    def get_employee_code(self):
        for case in self:
            emp_code_sort = 0
            if case.emp_code:
                try:
                    emp_code_sort = int(case.emp_code)
                except:
                    emp_code_sort = 0
            case.emp_code_sort = emp_code_sort

    @api.one
    @api.depends('availed_leave', 'used_leave')
    def _compute_balance_leave(self):
        self.balance_leave = self._compute_leave(self) - self.used_leave

    #INHERITED
    name = fields.Char(string='Employee Name')
    company_id = fields.Many2one(string='Payroll Company')
    address_home_id = fields.Many2one(groups="base.group_user")

    # namee = fields.Char(string='Specify if the Employee ID.', required=True)
    @api.multi
    @api.depends('name', 'write_date')
    def get_joined_date(self):
        for case in self:
            joined_date = False
            if case.aj_date:
                joined_date = case.aj_date
                # joined_date = datetime.strptime(joined_date, '%Y-%m-%d')
                joined_date = joined_date.strftime('%Y-%m-%d %H:%M:%S')
            case.joined_date = joined_date

    joined_date = fields.Datetime(string='Computed Joining Date', compute="get_joined_date", store=True)
    name_arabic = fields.Char(string='Name in Arabic')
    family_ids = fields.One2many('hr.family.details','employee_id','Family Details',
                                 help="This includeds IQAMA details")
    address_ksa =fields.Char('Address in KSA')
    address_home =fields.Char('Address in Home Country')
    religion = fields.Selection([('muslim', 'Muslim'), ('non_muslim', 'Non Muslim')],default='muslim'
                                , string='Religion'
                                , track_visibility='onchange', help='Specify Religion of Employee.', required=True)
    emp_code_sort = fields.Integer(string='Employee Code Used For Sorting', compute='get_employee_code', store=True)
    emp_code = fields.Char(string='Employee Code', required=True)
    expiry_detail_ids = fields.One2many('hr.expiry.details', 'employee_id', 'Expiry Details')

    type_id = fields.Many2one('hr.employee.type', string="Type")
    availed_leave = fields.Float(string='Availed Leave', readonly=True, compute='_compute_availed_leave',
                                 digits=dp.get_precision('Decimal Single'))
    used_leave = fields.Float(string='Used Leave', readonly=True, digits=dp.get_precision('Decimal Single'))
    balance_leave = fields.Float(string='Balance Leave', readonly=True, compute='_compute_balance_leave',
                                 digits=dp.get_precision('Decimal Single'))

    no_payroll = fields.Boolean('No Payroll', help="Specify if the No Payroll.")
    aj_date = fields.Date(string='Date of Joined')
    birthday = fields.Date('Date of Birth', groups='base.group_user')
    ssnid = fields.Char('SSN No', help='Social Security Number', groups='base.group_user')
    sinid = fields.Char('SIN No', help='Social Insurance Number', groups='base.group_user')
    identification_id = fields.Char(string='Identification No', groups='base.group_user')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups='base.group_user')
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups='base.group_user')
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account Number',
        domain="[('partner_id', '=', address_home_id)]", help='Employee bank salary account', groups='base.group_user')
    work_status = fields.Selection(
        [('working', 'Working'), ('vacation', 'Vacation'), ('fired', 'Fired'), ('escape', 'Escape'),
         ('exit', 'Final Exit')], string='Work Status', required=True, default='working')
    sponsor = fields.Selection([('oursponsor', 'Our Sponsor'), ('othersponsor', 'Other Sponsor')], 'Sponsor',
                               required=True, default='oursponsor')
    position_classification = fields.Many2one('hr.position.classifications', 'Position Classification', )
    sponsor_company_id = fields.Many2one('res.company', 'Sponsor Company', )
    document_count = fields.Integer(compute='_document_count', string='# Documents')
    contract_date = fields.Date('Contract Date')

    @api.multi
    def _document_count(self):
        for case in self:
            detail_ids = self.env['hr.expiry.details'].search([('employee_id', '=', case.id)])
            case.document_count = len(detail_ids)

    @api.multi
    def document_view(self):
        self.ensure_one()
        view_kanban_id  =self.env.ref('pioneer_HR_Employee.ce_hr_employee_expiry_details_kanban').id
        view_form_id  =self.env.ref('pioneer_HR_Employee.ce_hr_employee_expiry_details_form').id
        return {
            'name': _('Details'),
            'domain': [('employee_id', '=', self.id)],
            'res_model': 'hr.expiry.details',
            'type': 'ir.actions.act_window',
            'views': [(view_kanban_id, 'kanban'), (view_form_id, 'form')],
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'limit': 80,
        }

    @api.model
    def default_get(self, fields):
        res = super(HrEmployee, self).default_get(fields)
        expiry_detail_list = []
        for ed in hg.EXPIRY_TYPE:
            expiry_detail_vals = {'type' : ed[0]}
            expiry_detail_list.append((0, 0, expiry_detail_vals))
        res.update({'expiry_detail_ids' : expiry_detail_list})
        return res

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     # TDE FIXME: currently overriding the domain; however as it includes a
    #     # search on a m2o and one on a m2m, probably this will quickly become
    #     # difficult to compute - check if performance optimization is required
    #     if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
    #         new_args = ['|','|',  ('name', operator, name), ('emp_code', operator, name), ('name_arabic', operator, name)]
    #     else:
    #         new_args = args
    #     return super(HrEmployee, self).name_search(name=name, args=new_args, operator=operator,
    #                                                          limit=limit)
    # OVERRIDDEN
    @api.multi
    def name_get(self):
        result = []
        for case in self:
            name = case.name or ''
            code = case.emp_code or ''
            if code:
                name = '[' + code + '] ' + name
            result.append((case.id, "%s" % (name and name or '',)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = dict(self._context or {})
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('name', '=', name)] + args, limit=limit)
        if not recs:
            domain = ['|','|',  ('name', operator, name+ '%'), ('emp_code', operator, name+ '%'), ('name_arabic', operator, name+ '%')]
            recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrEmployee, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        user = self.env.user
        if not user.is_hide_payslip: # show payslip smart button
            for node in doc.xpath("//button[@help='payslip']"):
              node.set('invisible', _('0'))
              setup_modifiers(node, res['fields'])
        res['arch'] = etree.tostring(doc)
        return res

    #  models.Model._get_external_ids(self)
    #SALAY RULES FUNCTIONALLITY START
    def _get_leave_data(self, aj_date, contract_date, contract_type, basic_contract_type):
        print ('aj_date, contract_date, contract_type, basic_contract_type',aj_date, contract_date, contract_type, basic_contract_type)
        #2017-01-01 False employee employee
        leave_earn = 0
        yearly_leave = 0
        now = datetime.now()
        if not aj_date:
            leave_earn = 0
            yearly_leave = 0
            return leave_earn, yearly_leave
        # aj_date = datetime.strptime(aj_date,'%Y-%m-%d') #2017-01-01
        months = (12 * now.year + now.month) - (12 * aj_date.year + aj_date.month) # (12 * 2019 + 2) - (12*2017+1) = 25
        if not basic_contract_type:
            leave_earn = 0
            yearly_leave = 0
            return leave_earn, yearly_leave
        if not contract_type:
            leave_earn = 0
            yearly_leave = 0
            return leave_earn, yearly_leave
        if basic_contract_type == contract_type:
            if basic_contract_type == 'employee':
                leave_earn = abs(months * 2.50) #62.5
                yearly_leave = 30
            elif basic_contract_type == 'worker':
                if months >= 60:
                    remonths = months - 60
                    fsec = abs(60 * 1.75)
                    ssec = abs(remonths * 2.50)
                    leave_earn = abs(fsec + ssec)
                    yearly_leave = 30
                else:
                    leave_earn = abs(months * 1.75)
                    yearly_leave = 21
            else:
                leave_earn = 0
                yearly_leave = 0
            return leave_earn, yearly_leave
        else:
            if not contract_date:
                if basic_contract_type == 'employee':
                    leave_earn = abs(months * 2.50)
                    yearly_leave = 30
                elif basic_contract_type == 'worker':
                    if months >= 60:
                        remonths = months - 60
                        fsec = abs(60 * 1.75)
                        ssec = abs(remonths * 2.50)
                        leave_earn = abs(fsec + ssec)
                        yearly_leave = 30
                    else:
                        leave_earn = abs(months * 1.75)
                        yearly_leave = 21
                else:
                    leave_earn = 0
                    yearly_leave = 0
            else:
                # contract_date = datetime.strptime(contract_date,'%Y-%m-%d')
                if now <= contract_date:
                    if basic_contract_type == 'employee':
                        leave_earn = abs(months * 2.50)
                        yearly_leave = 30
                    elif basic_contract_type == 'worker':
                        if months >= 60:
                            remonths = months - 60
                            fsec = abs(60 * 1.75)
                            ssec = abs(remonths * 2.50)
                            leave_earn = abs(fsec + ssec)
                            yearly_leave = 30
                        else:
                            leave_earn = abs(months * 1.75)
                            yearly_leave = 21
                    else:
                        leave_earn = 0
                        yearly_leave = 0
                else:
                    v1 = 0
                    v2 = 0
                    months1 = (12 * contract_date.year + contract_date.month) - (12 * aj_date.year + aj_date.month)
                    months2 = (12 * now.year + now.month) - (12 * contract_date.year + contract_date.month)
                    if basic_contract_type == 'employee':
                        v1 = abs(months1 * 2.50)
                    elif basic_contract_type == 'worker':
                        if months1 >= 60:
                            remonths = months1 - 60
                            fsec = abs(60 * 1.75)
                            ssec = abs(remonths * 2.50)
                            v1 = abs(fsec + ssec)
                        else:
                            v1 = abs(months1 * 1.75)
                    else:
                        leave_earn = 0
                    if contract_type == 'employee':
                        v2 = abs(months2 * 2.50)
                        yearly_leave = 30
                    elif contract_type == 'worker':
                        if months2 >= 60:
                            remonths = months2 - 60
                            fsec = abs(60 * 1.75)
                            ssec = abs(remonths * 2.50)
                            v2 = abs(fsec + ssec)
                            yearly_leave = 30
                        else:
                            v2 = abs(months2 * 1.75)
                            yearly_leave = 21
                    else:
                        leave_earn = 0
                        yearly_leave = 0
                    leave_earn = abs(v1 + v2)
            return leave_earn, yearly_leave

    def vacation_allowance_cal(self, employee, contract):
        total = 0
        total_salary = 0
        contract_obj = self.env['hr.contract']
        contract_ids = contract_obj.search([('employee_id','=', employee)])
        for record in contract_ids:
            total_salary = total_salary + record.wage + record.housing + record.living_cost + record.tuition + record.work + record.other

        leave_earn, yearly_leave = self._get_leave_data(self.aj_date or self.aj_date
                                                        , self.contract_date
                                                        , self.basic_contract_type
                                                        , self.basic_contract_type)
        if yearly_leave == 21:
            total = total_salary * 0.70 / 12
        elif yearly_leave == 30:
            total = total_salary * 1 / 12
        else:
            total = 0
        return total

    def eosb_cal(self, employee, date_from, date_to):
        print ('ffffffff')
        total = 0
        total_salary = 0
        eosb = 0
        contract_obj = self.env['hr.contract']
        contract_ids = contract_obj.search([('employee_id','=', employee)])
        for record in contract_ids:
            total_salary = total_salary + record.wage + record.housing + record.transportation + record.food + record.mobile + record.tuition + record.other
        sdate = self.aj_date or self.date_from# datetime.strptime(self.aj_date, '%Y-%m-%d') or datetime.strptime(date_from, '%Y-%m-%d')
        edate = date_to
        if sdate and edate:
            tday = edate
            sday = (tday - sdate).days
            sday = sday + 1
            if sday <= 1826 :
                eosb = (total_salary / 12) / 2
            else:
                eosb = total_salary / 12
        print('ffffffff2', eosb)
        return eosb

    def absent_cal(self, employee, date_from, date_to):
        total = 0
        total_salary = 0
        eosb = 0
        contract_obj = self.env['hr.contract']
        contract_ids = contract_obj.search([('employee_id', '=', employee)])
        for record in contract_ids:
            total_salary = total_salary + record.wage + record.housing + record.transportation + record.food + record.mobile + record.tuition + record.other
        if not self.aj_date:
            return 0
        sdate = self.aj_date
        edate = date_to
        if sdate and edate:
            tday = edate
            sday = (tday - sdate).days
            sday = sday + 1
            if sday <= 1826:
                eosb = (total_salary / 12) / 2
            else:
                eosb = total_salary / 12
        return eosb
    # SALARY RUKES FUNXITIONALITY END

    @api.multi
    def button_show_my_payslip(self):
        print('oooo')
        return {
                'name': _('Payslips'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hr.payslip',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('employee_id', '=', self.id)],
                'context' : {'search_default_employee_id': [self.id], 'default_employee_id': self.id}
               }

    #scheduler
    @api.model
    def run_reminder_about_employee_id_expiry(self):
        print (';ffffffffffffffffffffff')
        cr = self._cr
        sql = """select he.id as employee_id
                    , he.work_email
                    , ed.id as expiry_id
                    , r.name as employee_name
                    , ed.type as expiry_type
                  from hr_expiry_details ed 
                  inner join hr_employee he on he.id = ed.employee_id
                  inner JOIN resource_resource r on r.id = he.resource_id
                  where ed.expiry_date is not null 
                  and ed.expiry_date = now()::date 
                  and ed.is_reminder = True
                  and ed.is_reminder_mail_sent = False
                  """
        cr.execute(sql)
        Original_Data = cr.dictfetchall()
        for x in Original_Data:
            if x != None:
                template = self.env.ref('pioneer_HR_Employee.ps_email_template_employee_id_expiry', False)
                if x['expiry_type']:
                    template.subject = 'Employee-ID of Type - ' + (x['expiry_type'].upper()) + ' is going to expire.'
                template.send_mail(x['employee_id'], force_send=False, raise_exception=True)
                if x.get('expiry_id', False):
                    cr.execute("update hr_expiry_details set is_reminder_mail_sent = True where id = " + str(x['expiry_id']))

    #scheduler
    @api.model
    def run_reminder_about_list_employee_ids_expiry(self):
        cr = self._cr
        sql = """select he.id as employee_id
                    , he.work_email
                    , ed.id as expiry_id
                    , ed.type as expiry_type
                    , r.name as employee_name
                  from hr_expiry_details ed 
                  inner join hr_employee he on he.id = ed.employee_id
                  inner JOIN resource_resource r on r.id = he.resource_id
                  where ed.expiry_date is not null 
                      and ed.expiry_date = now()::date 
                      and ed.is_reminder = True
                      --and ed.is_reminder_mail_sent = False
                  """
        cr.execute(sql)
        Original_Data = cr.dictfetchall()
        employee_names = []
        employee_id = False
        for x in Original_Data:
            if x != None:
                employee_id = x.get('employee_id')
                employee_names.append(x.get('employee_name'))
        if employee_id and len(employee_names):
            employee_names = ','.join(employee_names)
            template = self.env.ref('pioneer_HR_Employee.ps_email_template_list_employee_ids_expiry', False)
            template.send_mail(employee_id, force_send=False, raise_exception=True)
            # template.body_html = template.body_html + ' \n Expiry Employee List :  ' + (len(employee_names) and str(employee_names) or '')
        # if x.get('expiry_id', False):
        #     cr.execute("update hr_expiry_details set is_reminder_mail_sent = True where id = " + str(x['expiry_id']))
