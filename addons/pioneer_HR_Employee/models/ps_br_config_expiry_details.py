# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
import time
import re
from odoo.tools import float_compare, float_is_zero
from odoo.addons.pioneer_HR_Employee.models import ps_br_hr_config_global as hg
from datetime import datetime

class hr_expiry_details(models.Model):
    _name = 'hr.expiry.details'
    _rec_name = 'type'
    _description = 'Expiry Details'

    employee_id = fields.Many2one('hr.employee','Employee')

    exp_id_no = fields.Char('ID/No.', required=False)
    # type = fields.Many2one('hr.id.type', 'Type')
    type = fields.Selection(hg.EXPIRY_TYPE, required=1)
    issue_date = fields.Date('Date of Issue')
    expiry_date = fields.Date('Date of Expiry')
    issue_place = fields.Char('Place of Issue')
    is_reminder = fields.Boolean("Expiry Reminder", default=False)
    is_reminder_mail_sent = fields.Boolean("Expiry Reminder Mail Sent?", default=False)
    issue_by = fields.Char('Issued By')
    note = fields.Char('Note')
    file = fields.Binary('File')
    filename = fields.Char('File')
    visa_type = fields.Selection([('visit', 'Visit'), ('temporary', 'Temporary'), ('permanent', 'Permanent'), ],
                                  'Visa Type', )
    visa_exit_date = fields.Date('Visa Exit Date')
    status = fields.Selection([('expiry', 'Expiry'), ('active', 'Active')], store=True, compute="check_expiry_status",
                              string='Status')


    @api.depends('expiry_date')
    def check_expiry_status(self):
        for case in self:
            is_expired = False
            if case.expiry_date:
                expiry_date = fields.Datetime.from_string(case.expiry_date)
                if datetime.today() > expiry_date:
                    is_expired = True
            case.status = is_expired and 'expiry' or 'active'
