# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning


class res_company(models.Model):
    _inherit = 'res.company'

    eosb_eosb_journal_id = fields.Many2one('account.journal', string='EOSB Journal',
                                           help="The journal used when the EOSB is done.")
