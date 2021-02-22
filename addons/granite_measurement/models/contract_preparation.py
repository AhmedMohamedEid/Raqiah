# -*- coding: utf-8 -*-
import logging
import psycopg2
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import base64
from lxml import etree
from odoo.osv.orm import setup_modifiers

_logger = logging.getLogger(__name__)


class ContractPreparation(models.Model):
    _name = 'contract.preparation'
    _description = 'Contract Preparation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True )
    date = fields.Date('Date', required=1, index=True, default=fields.Date.context_today )
    first_party = fields.Many2one('res.partner', 'Partner')
    second_party = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id )
    remarks = fields.Text('Remarks')
    description = fields.Text('Terms/Conditions')
    sub_total_contract = fields.Float('Sub Total Contract', compute='_amount_all', store=True)
    vat = fields.Float('Vat%5')
    total_contract = fields.Float('Total Contract', compute='_amount_total')
    payment_received = fields.Float('Payment Received')
    payment_remaining = fields.Float('Payment Remaining')
    contract_preparation_line = fields.One2many('contract.preparation.line', 'contract_preparation_id', 'Contract Line')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id )
    sale_order_id = fields.Many2one('sale.order', 'Sales Order')

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     user = self.env.user
    #     res = super(ContractPreparation, self).fields_view_get(view_id=view_id, view_type=view_type,
    #                                                            toolbar=toolbar,
    #                                                            submenu=submenu)
    #     doc = etree.XML(res['arch'])
    #     for node in doc.xpath("//kanban") + doc.xpath("//form") + doc.xpath("//tree"):
    #         if user.id in (1, 2):
    #             node.set('create', _('true'))
    #             node.set('edit', _('true'))
    #             node.set('delete', _('true'))
    #         if user.is_contract_rw:
    #             node.set('edit', _('true'))
    #             node.set('create', _('false'))
    #         if user.is_contract_rwc:
    #             node.set('edit', _('true'))
    #             node.set('create', _('true'))
    #     res['arch'] = etree.tostring(doc)
    #     return res

    @api.depends('vat', 'total_contract')
    def _amount_total(self):
        self.total_contract = self.sub_total_contract + self.vat

    @api.onchange('vat', 'sub_total_contract')
    def _compute_percentage(self):
        self.vat = self.sub_total_contract * 5 / 100

    @api.depends('contract_preparation_line.total_meter', 'contract_preparation_line.per_meter_price')
    def _amount_all(self):
        for contract in self:
            sub_total = amount_total = amount_tax = 0.0
            for line in contract.contract_preparation_line:
                sub_total += line.per_meter_price
                amount_total += line.total_meter
                # ~ amount_tax += (line.per_meter_price + line.total_meter) * 5 /100
            contract.update({
                'sub_total_contract': sub_total + amount_total,
            })

    @api.one
    def button_confirm(self):
        self.state = 'confirm'

    @api.one
    def button_cancel(self):
        self.state = 'cancel'

    @api.one
    def button_reset_to_draft(self):
        if not self.env.user.has_group('granite_measurement.group_contract_preparation_manager'):
            raise UserError(_('You dont have permission to cancel this record'))
        self.state = 'draft'


class ContractPreparationLine(models.Model):
    _name = 'contract.preparation.line'
    _description = 'Contract Preparation Line'

    name = fields.Char('Contract')
    contract_preparation_id = fields.Many2one('contract.preparation', 'Contract Preparation')
    design = fields.Char('Design')
    color = fields.Char('Colour')
    color_number = fields.Char('Colour Number')
    per_meter_price = fields.Float('Per meter price')
    total_meter = fields.Float('Total Meter')
