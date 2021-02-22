from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # TODO : remove this try catch if you didnt face any issues
        employee_obj = self.env['hr.employee']
        uid = self.env.uid
        is_direct_manager = False
        is_coach = False
        # employee = user.employee_ids and user.employee_ids[0]
        direct_manager_ids = employee_obj.search([('parent_id.user_id', '=', uid)])
        if len(direct_manager_ids):
            is_direct_manager = True
        coach_ids = employee_obj.sudo().search([('coach_id.user_id','=',uid)])
        if len(coach_ids):
            is_coach = True
        try: #Hide a menu based on the value in company master
            my_leave_request_menu = self.env.ref('pioneer_HR_Leave.hr_holidays_saudi')
            d_mgr_leave_req_approval_menu = self.env.ref('pioneer_HR_Leave.hr_holidays_saudi_direct')
            team_mgr_leave_req_approval_menu = self.env.ref('pioneer_HR_Leave.hr_holidays_saudi_team')
            all_leave_request_approval_menu = self.env.ref('pioneer_HR_Leave.hr_holidays_saudi_hr')
            # no use
            officer_leave_request_approval_menu = self.env.ref('pioneer_HR_Leave.hr_holidays_saudi_officer')
            gm_leave_request_approval_menu = self.env.ref('pioneer_HR_Leave.hr_holidays_saudi_hr_gm')
            #
            group_user = self.user_has_groups('hr.group_user')
            group_hr_manager = self.user_has_groups('hr.group_hr_manager')
            if uid != 1:
                args = args + [('id', 'not in', [officer_leave_request_approval_menu.id,gm_leave_request_approval_menu.id])]
            if group_user and not group_hr_manager:
                args = args + [('id', 'not in', [d_mgr_leave_req_approval_menu.id,team_mgr_leave_req_approval_menu.id,all_leave_request_approval_menu.id])]
            # if group_hr_manager :
            if not is_direct_manager:
                args = args + [('id', 'not in', [d_mgr_leave_req_approval_menu.id])]
            print ('is_coachis_coach',is_coach)
            if not is_coach:
                args = args + [('id', 'not in', [team_mgr_leave_req_approval_menu.id])]

        except UserError as e:
            _logger.info('ERROR ON LOADING MENUS. ' + str(e))
            pass
        return super(IrUiMenu, self).search(args, offset=0, limit=None, order=order, count=False)
