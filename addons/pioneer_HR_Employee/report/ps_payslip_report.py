# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError


class Reportpayslip(models.AbstractModel):
    _name = 'report.payslip_report_xls_ps.report_payslip_ps'

    @api.model
    def get_report_values(self, docids, data=None):
        print("doc_ids....",docids)
        print("data....", data)
        print("context....", self._context)

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        clause = []
        sales_records = []
        orders = self.env['hr.payslip'].search([('company_id', '=', docs.company_id.id)])
        # if docs.date_from and docs.date_to:
        #     for order in orders:
        #         if parse(docs.date_from) <= parse(order.date_order) and parse(docs.date_to) >= parse(order.date_order):
        #             sales_records.append(order);
        # else:
        #     raise UserError("Please enter duration")
        clause += self._get_search_from_state(docs)
        clause += self._get_search_from_type(docs)
        payslip_ids = self.env['hr.payslip'].search(clause)
        if not payslip_ids:
            raise UserError('Null Data Record not found')

        #session_report = self.env['ir.actions.report']._get_report_from_name('payslip_report_xls_ps.report_payslip_ps')
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'payslips': payslip_ids,
            'orders': sales_records,
            'case': self
        }



    def _get_search_from_state(self, docs):
        search = [('date_from', '>=', docs.f_date),('date_to', '<=', docs.t_date),('company_id', '=', docs.company_id.id)]
        if docs.state != 'all':
            search += [('date_from', '>=', docs.f_date),('date_to', '<=', docs.t_date),
                       ('company_id', '=', docs.company_id.id),('state', '=', docs.state)]
        return search

    def _get_search_from_type(self, docs):
        search = []
        if docs.type == 'without_refund':
            search += [('credit_note', '=', False)]
        elif docs.type == 'only_refund':
            search += [('credit_note', '=', True)]
        return search

    @api.multi
    def get_rule(self,slip_id,rule):
        self._cr.execute("select total from hr_payslip_line where salary_rule_id in (select id from hr_salary_rule where lower(code) = '%s') and slip_id in (select id from hr_payslip where id = %s)" % (rule.lower(),slip_id))
        res = self._cr.fetchone()
        if res:
            return res[0]
        else:
            return 0.0

    @api.multi
    def get_total(self,slip_id):
        total = 0
        rule_type = ['loan', 'hrdf', 'advance', 'gosi', 'other_deduction', 'absent']
        for r in rule_type:
            res = self.get_rule(slip_id,r)
            if res:
                total = total + res
            else:
                total = total
        return total

    @api.multi
    def get_total_rule(self,rule,data):
        slip_obj = self.get_data(data)
        total = 0
        for slip_id in slip_obj:
            rule_amt = self.get_rule(slip_id.id,rule,data)
            if rule_amt != None:
                total = total + rule_amt
            else:
                total = total
        return total
