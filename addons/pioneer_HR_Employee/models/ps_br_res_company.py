# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from lxml import etree
from odoo.osv.orm import setup_modifiers
import logging
_logger = logging.getLogger(__name__)

class res_company(models.Model):
    _inherit = 'res.company'

    finance_manager_id = fields.Many2one('res.users', 'Finance Manager')

    @api.multi
    def button_apply_manager_to_all_company(self):
        company_obj = self.env['res.company']
        for case in self:
            company_ids = company_obj.sudo().search([])
            for company in company_ids:
                company.finance_manager_id = not company.finance_manager_id and case.finance_manager_id.id

