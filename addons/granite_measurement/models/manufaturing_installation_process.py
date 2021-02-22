# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from lxml import etree
from odoo.osv.orm import setup_modifiers

_logger = logging.getLogger(__name__)


class ManufacturingInstalltionProcess(models.Model):
    _name = 'manufacturing.installation.process'
    _description = 'Manufacturing Installtion Process'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', size=24)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
    country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
    phone = fields.Char('Phone')
    email = fields.Char('Email')
    mobile = fields.Char('Mobile')
    date = fields.Date('Date', required=1, index=True, default=fields.Date.context_today)
    file_no = fields.Char('File No')
    shop_name = fields.Char('Shop Name')
    kitchen_color = fields.Char('Kitchen Colour')
    granite_type = fields.Char('Granite Type')
    sink_type = fields.Char('Sink Type')
    cardboard_type = fields.Char('Cardboard Type')
    employee_for_installation = fields.Many2one('hr.employee', 'Employee for installation')
    missing_list_changes = fields.Char('Missing List/Changes')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     user = self.env.user
    #     res = super(ManufacturingInstalltionProcess, self).fields_view_get(view_id=view_id, view_type=view_type,
    #                                                                        toolbar=toolbar,
    #                                                                        submenu=submenu)
    #     doc = etree.XML(res['arch'])
    #     for node in doc.xpath("//kanban") + doc.xpath("//form") + doc.xpath("//tree"):
    #         if user.id in (1, 2):
    #             node.set("create", _('true'))
    #             node.set('edit', _('true'))
    #             node.set('delete', _('true'))
    #         if user.is_manufacturing_rw:
    #             node.set('edit', _('true'))
    #             node.set("create", _('false'))
    #         if user.is_manufacturing_rwc:
    #             node.set('edit', _('true'))
    #             node.set("create", _('true'))
    #     res['arch'] = etree.tostring(doc)
    #     return res
