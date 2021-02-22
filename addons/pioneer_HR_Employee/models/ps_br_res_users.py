# -*- coding: utf-8 -*-
from odoo import api, fields, models

class res_users(models.Model):
    _inherit = 'res.users'

    is_hide_payslip = fields.Boolean('Hide Payslip On Employee Form', default=False
                    , help="Show Payslip Button on this checkbox, Hide when it is checked")