# -*- coding: utf-8 -*-

from odoo import api, models, fields
import logging
import time

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    visit_date = fields.Date('Visit Date', required=True, default=time.strftime('%Y-%m-%d'))
    mobile = fields.Char(size=10, required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
