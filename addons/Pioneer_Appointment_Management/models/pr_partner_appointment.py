# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
import logging
import time
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class pr_partner_appointment(models.Model):
    _name = 'pr.partner.appointment'
    _inherit = ['mail.thread']

    def _get_time_values(self, context=None):
        time_set1 = [(str((r)).zfill(2) + '.00', str((r)).zfill(2) + ':00') for r in range(24)]
        time_set3 = [(str((r)).zfill(2) + '.30', str((r)).zfill(2) + ':30') for r in range(24)]
        time_set = time_set1 + time_set3
        return sorted(time_set, key=lambda x: x[1])

    @api.multi
    def get_partner_mobile(self):
        for case in self:
            partner = case.partner_id
            case.customer_mobile = partner.mobile or ''

    partner_id = fields.Many2one('res.partner', 'Customer', required=1)
    name = fields.Char('Name', required=0)
    appointment_date = fields.Date('Date', required=1, index=True, default=fields.Date.context_today)
    appointment_time = fields.Selection(_get_time_values(30), string='Appointment Time')
    customer_mobile = fields.Char(compute=get_partner_mobile, string='Mobile')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    co_ordination = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Co-ordination')
    remarks = fields.Text(string='Remarks')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('approve', 'Approved'), ('cancel', 'Cancel')],
                         string='Status', default='draft')


    @api.multi
    def action_confirm(self):
        for case in self:
            case.state = 'confirm'

    @api.multi
    def action_approve(self):
        for case in self:
            case.state = 'approve'

    @api.multi
    def action_cancel(self):
        for case in self:
            case.state = 'cancel'

    @api.multi
    def action_reset_to_draft(self):
        for case in self:
            case.state = 'draft'

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('pr.partner.appointment') or ' '
        res = super(pr_partner_appointment, self).create(values)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
