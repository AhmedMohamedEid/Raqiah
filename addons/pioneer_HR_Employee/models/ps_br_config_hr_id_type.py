# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
import time
import re
from odoo.tools import float_compare, float_is_zero

class HrIdType(models.Model):
    _name = 'hr.id.type'
    _rec_name = 'name'
    _description = 'Id Type Master'

    name = fields.Char('Name', required=True)
