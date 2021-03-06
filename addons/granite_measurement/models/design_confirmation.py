# -*- coding: utf-8 -*-
import logging
import psycopg2
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import base64
from lxml import etree
from odoo.osv.orm import setup_modifiers

_logger = logging.getLogger(__name__)


class DesignConfirmation(models.Model):
    _name = 'design.confirmation'
    _description = 'Design Confirmation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)
    customer_code = fields.Char('Customer Code')
    customer_details = fields.Many2one('res.partner', 'Customer Details')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', size=24)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
    country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
    phone = fields.Char('Phone')
    email = fields.Char('Email')
    mobile = fields.Char('Mobile')
    blue_print_receive_date = fields.Date('Blueprint Receive Date')
    designer_submission_date = fields.Date('Designer Submission Date')
    designer_receive_date = fields.Date('Designer Receive Date')
    designer_name = fields.Many2one('hr.employee', 'Designer Name')
    visit_day = fields.Date('Visit Day', required=1, index=True, default=fields.Date.context_today)
    date_signature = fields.Date('Date Signature', default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     user = self.env.user
    #     res = super(DesignConfirmation, self).fields_view_get(view_id=view_id, view_type=view_type,
    #                                                           toolbar=toolbar,
    #                                                           submenu=submenu)
    #     doc = etree.XML(res['arch'])
    #     for node in doc.xpath("//kanban") + doc.xpath("//form") + doc.xpath("//tree"):
    #         if user.id in (1, 2):
    #             node.set('create', _('true'))
    #             node.set('edit', _('true'))
    #             node.set('delete', _('true'))
    #         if user.is_design_rw:
    #             node.set('edit', _('true'))
    #             node.set('create', _('false'))
    #         if user.is_design_rwc:
    #             node.set('edit', _('true'))
    #             node.set('create', _('true'))
    #     res['arch'] = etree.tostring(doc)
    #     return res

    def _onchange_partner_id_values(self, partner_id):
        """ returns the new values when partner_id has changed """
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)

            partner_name = partner.parent_id.name
            if not partner_name and partner.is_company:
                partner_name = partner.name

            return {
                'customer_code': partner_name,
                # 'contact_name': partner.name if not partner.is_company else False,
                # 'title': partner.title.id,
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city,
                'state_id': partner.state_id.id,
                'country_id': partner.country_id.id,
                'email': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'zip': partner.zip,
                # 'function': partner.function,
                # 'website': partner.website,
            }
        return {}

    @api.onchange('customer_details')
    def _onchange_customer_details(self):
        values = self._onchange_partner_id_values(self.customer_details.id if self.customer_details else False)
        self.update(values)
