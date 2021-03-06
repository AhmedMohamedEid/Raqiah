# -*- coding: utf-8 -*-
from odoo import fields, models


class MapSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_enable_google_maps = fields.Boolean()
    google_maps_api_key = fields.Char('Google Maps API Key')

    def set_google_maps_api_key(self):
        self.env['ir.config_parameter'].set_param(
            'google_maps_api_key', (self.google_maps_api_key or '').strip(), groups=['base.group_system'])

    def get_default_google_maps_api_key(self, fields):
        google_maps_api_key = self.env['ir.config_parameter'].get_param('google_maps_api_key', default='')
        return dict(google_maps_api_key=google_maps_api_key)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: