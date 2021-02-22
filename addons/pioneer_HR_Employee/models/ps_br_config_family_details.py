# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
import time
import re
from odoo.tools import float_compare, float_is_zero

class hr_family_details(models.Model):
    _name = 'hr.family.details'
    _rec_name = 'name'
    _description = 'Family Details'

    #inherited
    name = fields.Char(string='Name', required=True, translate=True)

    employee_id = fields.Many2one('hr.employee','Employee')

    name_arabic = fields.Char(string='Name in Arabic')
    iqama_no = fields.Char('Iqama / National ID',size=10)
    dob = fields.Date('Date of Birth')
    marital = fields.Selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')],'Martial status')
    gender = fields.Selection([('male','Male'),('female','Female')],'Gender', default='male')
    relation_type = fields.Selection([('wife','Wife'),('son','Son'),('mother','Mother'),('father','Father'),('daughter','Daughter'),('brother','Brother'),('other','Other')],string='Relation Type')
    sponsor_name = fields.Char('Sponsor Name')
    sponsor_no = fields.Char('Sponsor Number')
    country_id = fields.Many2one('res.country', 'Country')
