# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from lxml import etree
from odoo.osv.orm import setup_modifiers
from odoo.addons.pioneer_HR_Employee.models import ps_br_hr_config_global as hg

class IrRule(models.Model):
    _inherit = 'ir.rule'

 #   @api.model
  #  def domain_get(self, model_name, mode='read'):
  #      context = dict(self._context or {})
  #      dom = self._compute_domain(model_name, mode)
  #      if dom:
            # _where_calc is called as superuser. This means that rules can
            # involve objects on which the real uid has no acces rights.
            # This means also there is no implicit restriction (e.g. an object
            # references another object the user can't see).
  #          if model_name == 'hr.employee':
   #             dom = hg.return_employee_domain(self, context, dom)

            # print ('domdomdom',model_name,dom)
    #        query = self.env[model_name].sudo()._where_calc(dom, active_test=False)
     #       return query.where_clause, query.where_clause_params, query.tables
   #     return [], [], ['"%s"' % self.env[model_name]._table]

