# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def default_get(self, default_fields):
        res = super(AccountInvoice, self).default_get(default_fields)
        branch_id = False
        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({
            'branch_id' : branch_id
        })
        return res


    branch_id = fields.Many2one('res.branch', string="Branch")


    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        result = super(AccountInvoice, self).action_move_create()

        for invoice in self:
            if invoice.move_id:
                move_id = invoice.move_id
                branch_id = False
                if invoice.branch_id:
                    branch_id = invoice.branch_id.id
                elif self.env.user.branch_id:
                    branch_id = self.env.user.branch_id.id

                move_id.write({'branch_id' : branch_id})
                for move in move_id.line_ids:
                    move.write({'branch_id' : branch_id})
            
        return result

    @api.model
    def tax_line_move_line_get(self):
        result = super(AccountInvoice, self).tax_line_move_line_get()
        for res in result:
            branch_id = False
            if self.branch_id:
                branch_id = self.branch_id.id
            res.update({
                'branch_id' : branch_id
                })
        return result


    @api.model
    def _anglo_saxon_purchase_move_lines(self, i_line, res):
        """Return the additional move lines for purchase invoices and refunds.

        i_line: An account.invoice.line object.
        res: The move line entries produced so far by the parent move_line_get.
        """
        result = super(AccountInvoice, self)._anglo_saxon_purchase_move_lines(i_line, res)

        if result:
            for res in result:
                branch_id = False
                if self.branch_id:
                    branch_id = self.branch_id.id
                res.update({'branch_id' : branch_id})

        return result


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def default_get(self, default_fields):
        res = super(AccountMove, self).default_get(default_fields)
        branch_id = False
        if self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({'branch_id' : branch_id})
        return res

    branch_id = fields.Many2one('res.branch', string="Branch")

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def default_get(self, default_fields):
        res = super(AccountMoveLine, self).default_get(default_fields)
        branch_id = False
        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({'branch_id' : branch_id})
        return res

    branch_id = fields.Many2one('res.branch', string="Branch")
