# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    eosb_emp_type_id = fields.Many2one('eosb.emp.type', string="EOSB Category", domain=[('state', '=', 'active')])



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
