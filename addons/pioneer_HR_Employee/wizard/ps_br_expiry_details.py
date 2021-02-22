import time
from odoo import api, models, fields,_
from datetime import datetime
from dateutil import relativedelta
from dateutil.parser import parse
from odoo.exceptions import UserError
import base64

class ps_br_expiry_details_report_wiz(models.TransientModel):
    _name = "ps.br.expiry.details.report.wiz"

    comparison_date = fields.Date('Date to be expired', help='Expiry date <= the entered date'
                                  , required=True,default=lambda *a: time.strftime('%Y-%m-01'))
    company_id = fields.Many2one('res.company', 'Company', required=True,default=lambda self: self.env.user.company_id)
    # report_type = fields.Selection([('pdf','PDF'),('xls','XLS')],'Report Type', default='pdf')


    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['comparison_date', 'company_id'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['comparison_date', 'company_id'])[0])
        return self.env.ref("pioneer_HR_Employee.ps_br_action_expiry_details_report").with_context(landscape=True).report_action(self, data=data)

    # @api.multi
    # def check_wages_report(self):
    #     data = {}
    #     data['form'] = self.read(['f_date', 't_date', 'company_id', 'type', 'state'])[0]
    #     return self.get_wages_xls_data(data['form'])

    
    # @api.multi
    # def get_xls_data(self, data):
    #     clause = [('company_id', '=', self.company_id.id)]
    #     clause += self.get_search_from_state()
    #     clause += self.get_search_from_type()
    #     payslip_ids = self.env['hr.payslip'].search(clause)
    #     if not payslip_ids:
    #         raise UserError('Null Data Record not found')
    #
    #
    #     rec_string = payslip_ids._ids
    #
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': '/web/binary/download_document?model=hr.payslip&field=datas&id=%s&filename=Payslip.xls&wiz_id=%s' % (
    #             str(rec_string), self.ids),
    #         'target': 'new',
    #         'tag': 'reload',
    #     }
    #
    # @api.multi
    # def get_wages_xls_data(self, data):
    #     clause = [('company_id', '=', self.company_id.id)]
    #     clause += self.get_search_from_state()
    #     clause += self.get_search_from_type()
    #     payslip_ids = self.env['hr.payslip'].search(clause)
    #     if not payslip_ids:
    #         raise UserError('Null Data Record not found')
    #
    #     rec_string = payslip_ids._ids
    #
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': '/web/binary/download_document?model=hr.payslip&field=datas&id=%s&filename=Payslip.xls&wiz_id=%s&from=wages' % (
    #             str(rec_string), self.ids),
    #         'target': 'new',
    #         'tag': 'reload',
    #     }
    #
    #
    # def get_search_from_state(self):
    #     search = [('date_from', '>=', self.f_date), ('date_to', '<=', self.t_date),
    #               ('company_id', '=', self.company_id.id)]
    #     if self.state != 'all':
    #         search += [('date_from', '>=', self.f_date), ('date_to', '<=', self.t_date),
    #                    ('company_id', '=', self.company_id[0]), ('state', '=', self.state)]
    #     return search
    #
    # def get_search_from_type(self):
    #     search = []
    #     if self.type == 'without_refund':
    #         search += [('credit_note', '=', False)]
    #     elif self.type == 'only_refund':
    #         search += [('credit_note', '=', True)]
    #     return search
        