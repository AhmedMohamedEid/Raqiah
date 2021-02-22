# -*- coding: utf-8 -*-
from odoo import models, fields, api


class contractPreparation(models.Model):
    _inherit = 'contract.preparation'

    houd = fields.Char()  # الحوض
    shifa = fields.Char()  # نزول الشفة
    nozol = fields.Char()  # نزول
    color = fields.Char()  # لون الرخام
    hinges = fields.Char()  # المفصلات
    base = fields.Char()  # القاعده
    dalfa = fields.Char()  # الدلفة
    number = fields.Char()  # رقم اللون
    kitchen_type = fields.Char()  # نوع المطبخ
    chatter = fields.Char()  # الماسكة
    sheelf = fields.Char()  # الرف

    financial_value = fields.Float()
    value_added_tax = fields.Float(compute='_get_value_added_tax')
    total_value_of_contract = fields.Float(compute='_get_value_added_tax')

    @api.one
    @api.depends('financial_value')
    def _get_value_added_tax(self):
        self.value_added_tax = (self.financial_value / 100) * 15
        self.total_value_of_contract = self.financial_value + self.value_added_tax
