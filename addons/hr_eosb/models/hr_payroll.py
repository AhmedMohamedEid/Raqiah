# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import except_orm, Warning, RedirectWarning


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    eosb_rules_ids = fields.Many2many('hr.salary.rule', string="Payslip Rule EOSB", readonly=True,
                                      states={'draft': [('readonly', False)]})
    eosb = fields.Boolean(string="EOSB", readonly=True,
                          states={'draft': [('readonly', False)]})
    eosb_days = fields.Integer(string="EOSB Days", readonly=True,
                               states={'draft': [('readonly', False)]})

#
#     @api.v7
#     def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):
#         def _sum_salary_rule_category(localdict, category, amount):
#             if category.parent_id:
#                 localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
#             localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
#             return localdict
#
#         class BrowsableObject(object):
#             def __init__(self, pool, cr, uid, employee_id, dict):
#                 self.pool = pool
#                 self.cr = cr
#                 self.uid = uid
#                 self.employee_id = employee_id
#                 self.dict = dict
#
#             def __getattr__(self, attr):
#                 return attr in self.dict and self.dict.__getitem__(attr) or 0.0
#
#         class InputLine(BrowsableObject):
#             """a class that will be used into the python code, mainly for usability purposes"""
#             def sum(self, code, from_date, to_date=None):
#                 if to_date is None:
#                     to_date = datetime.now().strftime('%Y-%m-%d')
#                 result = 0.0
#                 self.cr.execute("SELECT sum(amount) as sum\
#                             FROM hr_payslip as hp, hr_payslip_input as pi \
#                             WHERE hp.employee_id = %s AND hp.state = 'done' \
#                             AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
#                            (self.employee_id, from_date, to_date, code))
#                 res = self.cr.fetchone()[0]
#                 return res or 0.0
#
#         class WorkedDays(BrowsableObject):
#             """a class that will be used into the python code, mainly for usability purposes"""
#             def _sum(self, code, from_date, to_date=None):
#                 if to_date is None:
#                     to_date = datetime.now().strftime('%Y-%m-%d')
#                 result = 0.0
#                 self.cr.execute("SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours\
#                             FROM hr_payslip as hp, hr_payslip_worked_days as pi \
#                             WHERE hp.employee_id = %s AND hp.state = 'done'\
#                             AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
#                            (self.employee_id, from_date, to_date, code))
#                 return self.cr.fetchone()
#
#             def sum(self, code, from_date, to_date=None):
#                 res = self._sum(code, from_date, to_date)
#                 return res and res[0] or 0.0
#
#             def sum_hours(self, code, from_date, to_date=None):
#                 res = self._sum(code, from_date, to_date)
#                 return res and res[1] or 0.0
#
#         class Payslips(BrowsableObject):
#             """a class that will be used into the python code, mainly for usability purposes"""
#
#             def sum(self, code, from_date, to_date=None):
#                 if to_date is None:
#                     to_date = datetime.now().strftime('%Y-%m-%d')
#                 self.cr.execute("SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
#                             FROM hr_payslip as hp, hr_payslip_line as pl \
#                             WHERE hp.employee_id = %s AND hp.state = 'done' \
#                             AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s",
#                             (self.employee_id, from_date, to_date, code))
#                 res = self.cr.fetchone()
#                 return res and res[0] or 0.0
#
#         #we keep a dict with the result because a value can be overwritten by another rule with the same code
#         result_dict = {}
#         rules = {}
#         categories_dict = {}
#         blacklist = []
#         payslip_obj = self.pool.get('hr.payslip')
#         inputs_obj = self.pool.get('hr.payslip.worked_days')
#         obj_rule = self.pool.get('hr.salary.rule')
#         payslip = payslip_obj.browse(cr, uid, payslip_id, context=context)
#         worked_days = {}
#         for worked_days_line in payslip.worked_days_line_ids:
#             worked_days[worked_days_line.code] = worked_days_line
#         inputs = {}
#         for input_line in payslip.input_line_ids:
#             inputs[input_line.code] = input_line
#
#         categories_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, categories_dict)
#         input_obj = InputLine(self.pool, cr, uid, payslip.employee_id.id, inputs)
#         worked_days_obj = WorkedDays(self.pool, cr, uid, payslip.employee_id.id, worked_days)
#         payslip_obj = Payslips(self.pool, cr, uid, payslip.employee_id.id, payslip)
#         rules_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, rules)
#
#         baselocaldict = {'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj, 'worked_days': worked_days_obj, 'inputs': input_obj}
#         #get the ids of the structures on the contracts and their parent id as well
#         structure_ids = self.pool.get('hr.contract').get_all_structures(cr, uid, contract_ids, context=context)
#         #get the rules of the structure and thier children
#         rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
#         #run the rules by sequence
#         if len(payslip.eosb_rules_ids) > 0:
#             rule_ids = self.pool.get('hr.salary.rule')._recursive_search_of_rules(cr, uid, payslip.eosb_rules_ids, context=context)
# #        raise Warning(_(rule_ids))
#
#         sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
#
#
#         for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
#             employee = contract.employee_id
#             localdict = dict(baselocaldict, employee=employee, contract=contract)
#             for rule in obj_rule.browse(cr, uid, sorted_rule_ids, context=context):
#                 key = rule.code + '-' + str(contract.id)
#                 localdict['result'] = None
#                 localdict['result_qty'] = 1.0
#                 localdict['result_rate'] = 100
#                 #check if the rule can be applied
#                 if obj_rule.satisfy_condition(cr, uid, rule.id, localdict, context=context) and rule.id not in blacklist:
#                     #compute the amount of the rule
#                     amount, qty, rate = obj_rule.compute_rule(cr, uid, rule.id, localdict, context=context)
#                     #check if there is already a rule computed with that code
#                     previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
#                     #set/overwrite the amount computed for this rule in the localdict
#                     tot_rule = amount * qty * rate / 100.0
#                     localdict[rule.code] = tot_rule
#                     rules[rule.code] = rule
#                     #sum the amount for its salary category
#                     localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
#                     #create/overwrite the rule in the temporary results
#                     result_dict[key] = {
#                         'salary_rule_id': rule.id,
#                         'contract_id': contract.id,
#                         'name': rule.name,
#                         'code': rule.code,
#                         'category_id': rule.category_id.id,
#                         'sequence': rule.sequence,
#                         'appears_on_payslip': rule.appears_on_payslip,
#                         'condition_select': rule.condition_select,
#                         'condition_python': rule.condition_python,
#                         'condition_range': rule.condition_range,
#                         'condition_range_min': rule.condition_range_min,
#                         'condition_range_max': rule.condition_range_max,
#                         'amount_select': rule.amount_select,
#                         'amount_fix': rule.amount_fix,
#                         'amount_python_compute': rule.amount_python_compute,
#                         'amount_percentage': rule.amount_percentage,
#                         'amount_percentage_base': rule.amount_percentage_base,
#                         'register_id': rule.register_id.id,
#                         'amount': amount,
#                         'employee_id': contract.employee_id.id,
#                         'quantity': qty,
#                         'rate': rate,
#                     }
#                     if payslip.eosb_days > 0:result_dict[key].update({'amount': ((amount/30) * payslip.eosb_days)})
#                 else:
#                     #blacklist this rule and its children
#                     blacklist += [id for id, seq in self.pool.get('hr.salary.rule')._recursive_search_of_rules(cr, uid, [rule], context=context)]
#
#         result = [value for code, value in result_dict.items()]
#         return result
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
