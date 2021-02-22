# -*- coding: utf-8 -*-

from odoo import api, models, fields
import logging
import time

_logger = logging.getLogger(__name__)



class res_partner(models.Model):
    _inherit = 'res.partner'

    visit_date = fields.Date('Visit Date', required=True, default=time.strftime('%Y-%m-%d'))
    appoinment_ids = fields.One2many('pr.partner.appointment', 'partner_id', string='Appointments')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
