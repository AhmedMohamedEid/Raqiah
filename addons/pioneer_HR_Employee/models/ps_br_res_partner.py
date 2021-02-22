# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from lxml import etree
from odoo.osv.orm import setup_modifiers
import logging
_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.depends('write_date')
    @api.multi
    def check_is_user(self):
        user_obj = self.env['res.users']
        for case in self:
            if case.name and case.id:
                is_user = False
                user_ids = user_obj.search([('partner_id','=',case.id)])
                if len(user_ids) > 0:
                    is_user = True
                case.is_user = is_user

    @api.depends('name')
    @api.multi
    def check_is_employee(self):
        employee_obj = self.env['hr.employee']
        cr =self._cr
        loop = 1
        for case in self:
            if case.name and case.id:
                _logger.info('Computing Partner Name and count ===========> ' + str(loop) + ' ' + str(case.name))
                is_employee = False
                # employee_ids = employee_obj.search([('address_home_id','=',case.id)])
                sql = "select id from hr_employee where address_home_id = " + str(case.id)
                cr.execute(sql)
                employee_ids = [x.get('id') for x in cr.dictfetchall()]
                if employee_ids != None and len(employee_ids) > 0:
                    is_employee = True
                case.is_employee = is_employee
                loop = loop + 1

    is_user = fields.Boolean(compute='check_is_user', store=True, string='Is User?')
    is_employee = fields.Boolean(compute='check_is_employee', store=True, string='Is Employee?')
