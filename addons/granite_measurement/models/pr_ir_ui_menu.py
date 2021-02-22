from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.multi
    def _filter_visible_menus(self):
        self.clear_caches()
        res = super(IrUiMenu, self)._filter_visible_menus()
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # TODO : remove this try catch if you didnt face any issues
        user = self.env.user
        try:  # Hide a menu based on the value in company master
            if user.id not in (1, 2):
                hidden_menus = []
                if not user.is_granite:
                    hidden_menus.append(self.env.ref('granite_measurement.menu_granite_measurement').id)
                if not user.is_design:
                    hidden_menus.append(self.env.ref('granite_measurement.menu_design_confirmation').id)
                if not user.is_material:
                    hidden_menus.append(self.env.ref('granite_measurement.menu_material_details').id)
                if not user.is_contract:
                    hidden_menus.append(self.env.ref('granite_measurement.menu_contract_preparation').id)
                if not user.is_manufacturing:
                    hidden_menus.append(self.env.ref('granite_measurement.menu_manufacturing_installation_process').id)
                if not user.is_booking:
                    hidden_menus.append(self.env.ref('granite_measurement.menu_booking_for_installation').id)

                if not user.is_granite and not user.is_design and user.is_material \
                        and not user.is_contract and not user.is_manufacturing and not user.is_booking:
                    hidden_menus.append(self.env.ref('granite_measurement.menu_granite_measurements_root').id)
                args = args + [('id', 'not in', hidden_menus)]
        except UserError as e:
            _logger.info('ERROR ON LOADING MENUS. ' + str(e))
            pass
        return super(IrUiMenu, self).search(args, offset=0, limit=None, order=order, count=False)
