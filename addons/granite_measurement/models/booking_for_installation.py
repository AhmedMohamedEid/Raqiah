# -*- coding: utf-8 -*-
import logging
import psycopg2
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import base64
from lxml import etree
from odoo.osv.orm import setup_modifiers

_logger = logging.getLogger(__name__)


class BookingInstalltion(models.Model):
    _name = 'booking.installation'
    _description = 'Booking for installtion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)
    phone = fields.Char('Phone')
    shop_name = fields.Char('Shop Name')
    date = fields.Date('Date', required=1, index=True, default=fields.Date.context_today)
    day = fields.Integer('Day')
    type_of_work = fields.Char('Type of work')
    customer_details = fields.Char('Customer Details')
    aluminium = fields.Char('Aluminium')
    granite = fields.Char('Granite')
    confirm_reservation = fields.Char('Confirm Reservation')
    pay_of_customer = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Pay Of Customer 50%')
    review_with_contract_accounting = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                       string='Review Contract with Accouting')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     user = self.env.user
    #     res = super(BookingInstalltion, self).fields_view_get(view_id=view_id, view_type=view_type,
    #                                                           toolbar=toolbar,
    #                                                           submenu=submenu)
    #     doc = etree.XML(res['arch'])
    #     for node in doc.xpath("//kanban") + doc.xpath("//form") + doc.xpath("//tree"):
    #         if user.id in (1, 2):
    #             node.set('create', _('true'))
    #             node.set('edit', _('true'))
    #             node.set('delete', _('true'))
    #         if user.is_booking_rw:
    #             node.set('edit', _('true'))
    #             node.set('create', _('false'))
    #         if user.is_booking_rwc:
    #             node.set('edit', _('true'))
    #             node.set('create', _('true'))
    #     res['arch'] = etree.tostring(doc)
    #     return res
