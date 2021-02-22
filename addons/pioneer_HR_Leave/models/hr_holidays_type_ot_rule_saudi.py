# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime,timedelta
from lxml import etree, html

import math
import collections
# try:
#     from service_solutions.common_ps.models.nazar import mail_create, get_email_from, get_config
# except:
#     try:
#         from odoo.common_ps.models.nazar import mail_create, get_email_from, get_config
#     except:
#         from odoo.addons.common_ps.models.nazar import mail_create, get_email_from, get_config

from odoo import SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from odoo.addons.pioneer_HR_Employee.models import ps_br_hr_config_global as hg


class hr_holidays_type_ot_rule_saudi(models.Model):
    _name = 'hr.holidays.type.ot.rule.saudi'
    _inherit = ['mail.thread', 'resource.mixin']

    type_id = fields.Many2one('hr.holidays.type.saudi', string='Type Reference', ondelete='cascade', index=True)
    days = fields.Float(string='Hours', required=True)
    percentage = fields.Float(string='Deduction Hours', required=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ],
            'Status', readonly=True, track_visibility='onchange', default='draft')




     
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
