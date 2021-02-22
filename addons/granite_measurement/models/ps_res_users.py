# -*- coding: utf-8 -*-

from odoo import api, models, fields
import logging

_logger = logging.getLogger(__name__)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class res_users(models.Model):
    _inherit = "res.users"

    is_granite = fields.Boolean('Granite Measurement', default=True, help="""""")
    is_granite_rw = fields.Boolean('Granite Measurement RW', default=True,
                                   help="""Edit Permission For Granite Measurement """)
    is_granite_rwc = fields.Boolean('Granite Measurement RWC', default=False,
                                    help="""Create Permission For Granite Measurement""")
    is_design = fields.Boolean('Design Confirmation', default=True, help="""""")
    is_design_rw = fields.Boolean('Design Confirmation RW', default=True,
                                  help="""Edit Permission For Design Confirmation""")
    is_design_rwc = fields.Boolean('Design Confirmation RWC', default=False,
                                   help="""Create Permission For Design Confirmation""")
    is_material = fields.Boolean('Material Details', default=True, help="""""")
    is_material_rw = fields.Boolean('Material Details RW', default=True,
                                    help="""Edit Permission For Material Details""")
    is_material_rwc = fields.Boolean('Material Details RWC', default=False,
                                     help="""Create Permission For Material Details""")
    is_contract = fields.Boolean('Contract Preparations', default=True, help="""""")
    is_contract_rw = fields.Boolean('Contract Preparations RW', default=True,
                                    help="""Edit Permission For Contract Preparations""")
    is_contract_rwc = fields.Boolean('Contract Preparations RWC', default=False,
                                     help="""Create Permission For Contract Preparations""")
    is_manufacturing = fields.Boolean('Manufacturing Installtion Process', default=True, help="""""")
    is_manufacturing_rw = fields.Boolean('Manufacturing Installtion Process RW', default=True,
                                         help="""Edit Permission For Manufacturing Installtion Process""")
    is_manufacturing_rwc = fields.Boolean('Manufacturing Installtion Process RWC', default=False,
                                          help="""Create Permission For Manufacturing Installtion Process""")
    is_booking = fields.Boolean('Booking For Installation', default=True, help="""""")
    is_booking_rw = fields.Boolean('Booking For Installation RW', default=True,
                                   help="""Edit Permission For Booking For Installation""")
    is_booking_rwc = fields.Boolean('Booking For Installation RWC', default=False, help="""""")
