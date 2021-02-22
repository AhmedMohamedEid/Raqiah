# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from lxml import etree
from odoo.osv.orm import setup_modifiers

_logger = logging.getLogger(__name__)


class MaterialDetail(models.Model):
    _name = 'material.detail'
    _description = 'Material in Detail'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)
    sales_person = fields.Many2one('res.users', 'Sales Person', default=lambda self: self._uid)
    shop_name = fields.Char('Shop Name')
    customer_name = fields.Many2one('res.partner', 'Customer Name')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', size=24)
    city = fields.Char('City')
    email = fields.Char('Email')
    mobile = fields.Char('Mobile')
    state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
    country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
    phone = fields.Char('Phone')
    device_measurement = fields.Char('Device Measurement')
    supplier_company = fields.Many2one('res.company', 'Supplier Company', default=lambda self: self.env.user.company_id)
    device_code = fields.Char('Device Code')
    sale_price = fields.Float('Sale Price')
    before_discount = fields.Float('Before Discount')
    after_discount = fields.Float('After Discount')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     user = self.env.user
    #     res = super(MaterialDetail, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
    #                                                       submenu=submenu)
    #     doc = etree.XML(res['arch'])
    #     for node in doc.xpath("//kanban") + doc.xpath("//form") + doc.xpath("//tree"):
    #         if user.id in (1, 2):
    #             node.set('create', _('true'))
    #             node.set('edit', _('true'))
    #             node.set('delete', _('true'))
    #         if user.is_material_rw:
    #             node.set('edit', _('true'))
    #             node.set('create', _('false'))
    #         if user.is_material_rwc:
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
                'shop_name': partner_name,
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

    @api.onchange('customer_name')
    def _onchange_customer_name(self):
        values = self._onchange_partner_id_values(self.customer_name.id if self.customer_name else False)
        self.update(values)
