# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class hr_leave_config_settings(models.TransientModel):
    _name = 'hr.leave.config.settings'
    _inherit = 'res.config.settings'

    def _get_values(self):
        return self.env['hr.leave.config.settings'].search([], limit=1, order='id desc')

    def _get_annual_leave(self):
        config = self._get_values()
        if config:return config.annual_leave
        return False

    def _get_annual_doj(self):
        config = self._get_values()
        if config:return config.annual_leave_doj
        return False

    def _get_managers_ids(self):
        return self.env['hr.leave.config.settings'].search([], limit=1, order='id desc')

    @api.constrains('managers_ids')
    def _managers_constrains(self):
        val = []
        for manager in self.managers_ids:
            if not manager.work_email: val.append(manager.name)
        if val: raise Warning(_('The following managers are dont have an Email ID! %s') % val)

    annual_leave = fields.Boolean(string='Enable Annual Leave Validation( 30 + 5)',default=_get_annual_leave)
    annual_leave_doj = fields.Boolean(string='Enable Annual Leave based on DOJ',default=_get_annual_doj)
    managers_ids = fields.Many2many('hr.employee',default=_get_managers_ids)