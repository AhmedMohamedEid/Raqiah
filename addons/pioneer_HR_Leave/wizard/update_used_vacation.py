# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class update_used_vacation(models.TransientModel):
    _name = 'update.used.vacation'

    def _default_employee(self):
        return self.env['hr.employee'].browse(self._context.get('active_id'))

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, default=_default_employee)
    used_vacation_days = fields.Float(string='Days', required=True)
    update_type = fields.Selection([('last_vacation_date', 'Last Vacation Date'), ('manual', 'Manual')],
                                    string='Update Type', default='last_vacation_date', required=True)
    last_vacation_date = fields.Date('Last Vacation Date')

    @api.multi
    def action_apply(self):
        cr =self._cr
        for case in self:
            employee = case.employee_id
            if case.update_type == 'last_vacation_date':
                if not case.last_vacation_date:
                    msg= 'Null Value \n Choose Last Vacation Date....'
                    raise UserError(_(msg))
                if not employee.aj_date:
                    msg = 'Null Value \n The Employee Has Not Date of Joining.'
                    raise UserError(_(msg))
                if not employee.yearly_vacation_days:
                    msg = 'Null Value \n The Employee Does Not Have Yearly Vacation Days.'
                    raise UserError(_(msg))

                aj_date = employee.aj_date
                yearly_vacation_days = employee.yearly_vacation_days

                # aj_date = datetime.strptime(aj_date, '%Y-%m-%d')
                last_vacation_date = case.last_vacation_date#datetime.strptime(case.last_vacation_date, '%Y-%m-%d')
                months = (12 * last_vacation_date.year + last_vacation_date.month) - (12 * aj_date.year + aj_date.month)
                if yearly_vacation_days == '21':
                    used_vacation_days = abs(months * 1.75)
                else:
                    used_vacation_days = abs(months * 2.50)
                sql = """update hr_employee set used_leave = %s,last_vacation_date = '%s' 
                          where id = %s""" % (abs(used_vacation_days), case.last_vacation_date, employee.id)
                cr.execute(sql)
            else:
                cr.execute("update hr_employee set used_leave = %s where id = %s" % (case.used_vacation_days, employee.id))
        return True



