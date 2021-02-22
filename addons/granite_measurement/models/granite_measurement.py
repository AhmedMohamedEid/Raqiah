# -*- coding: utf-8 -*-
import logging

from lxml import etree

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class GraniteMeasurementDetails(models.Model):
    _name = 'granite.measurement.details'
    _description = "Granite Measurement Details"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', size=24)
    city = fields.Char('City')
    mobile = fields.Char('Mobile')
    phone = fields.Char('Phone')
    place_of_depth = fields.Char('Place df depth')
    email = fields.Char('Email')
    shop_name = fields.Char('Shop name')
    granite_color = fields.Char('Granite Color')
    depth_measurement = fields.Char('Depth Measurement')
    side = fields.Char('Side')
    sink_measurement = fields.Char('Sink measurement')
    colour_of_sink = fields.Char('Colour of sink')
    depth_of_sink = fields.Char('Depth of sink')
    line = fields.Char('Line')
    contour = fields.Char('Contour')
    contour_of_depth = fields.Char('Contour depth')
    column = fields.Char('Column')
    oven = fields.Char('Oven')
    oven_type = fields.Char('Oven type')
    printer = fields.Char('Printer')
    coming_down = fields.Char()
    side_descending_places = fields.Char()
    connubial = fields.Char()
    side_slippers = fields.Char()


    # Relational fields
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
    country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
    type_of_sink = fields.Many2one('type.sink', string='Type of sink')
    supplier_company = fields.Many2one('res.company', 'Supplier company')
    partner_id = fields.Many2one('res.partner', 'Customer name')

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     user =self.env.user
    #     res = super(GraniteMeasurementDetails, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
    #                                                       submenu=submenu)
    #     doc = etree.XML(res['arch'])
    #     for node in doc.xpath("//kanban") + doc.xpath("//form") + doc.xpath("//tree"):
    #         if user.id in (1,2):
    #             node.set('create', _('true'))
    #             node.set('edit', _('true'))
    #             node.set('delete', _('true'))
    #         if user.is_granite_rw:
    #             node.set('edit', _('true'))
    #             node.set('create', _('false'))
    #         if user.is_granite_rwc:
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

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        values = self._onchange_partner_id_values(self.partner_id.id if self.partner_id else False)
        self.update(values)


class TypeOfSink(models.Model):
    _name = 'type.sink'
    _description = 'Type Of Sink'

    name = fields.Char('Type Of sink')
