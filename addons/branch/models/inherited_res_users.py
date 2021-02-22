# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    branch_ids = fields.Many2many('res.branch', string="Allowed Branch")
    branch_id = fields.Many2one('res.branch', string='Branch')

    @api.multi
    def write(self, values):
        if 'branch_id' in values or 'branch_ids' in values:
            self.env['ir.model.access'].sudo().call_cache_clearing_methods()
            self.env['ir.rule'].sudo().clear_caches()
            self.has_group.clear_cache(self)
        user = super(ResUsers, self).write(values)
        return user


class ir_sequence(models.Model):
    _inherit = 'ir.sequence'

    branch_id = fields.Many2one('res.branch', string='Branch')

    @api.model
    def next_by_code(self, sequence_code):
        """ Draw an interpolated string using a sequence with the requested code.
            If several sequences with the correct code are available to the user
            (multi-company cases), the one from the user's current company will
            be used.

            :param dict context: context dictionary may contain a
                ``force_company`` key with the ID of the company to
                use instead of the user's current company for the
                sequence selection. A matching sequence for that
                specific company will get higher priority.
        """
        self.check_access_rights('read')
        force_company = self._context.get('force_company')
        if not force_company:
            force_company = self.env.user.company_id.id
        seq_ids = self.search(
            [('code', '=', sequence_code), ('company_id', 'in', [force_company, False]),
             ('branch_id', 'in', [self.env.user.branch_id.id, False])],
            order='company_id')
        if not seq_ids:
            _logger.debug(
                "No ir.sequence has been found for code '%s'. Please make sure a sequence is set for current company." % sequence_code)
            return False
        seq_id = seq_ids[0]
        return seq_id._next()
