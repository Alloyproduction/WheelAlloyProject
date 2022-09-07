# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AlloyLeaveCustom(models.Model):
    _inherit = "hr.leave"


    leave_code = fields.Char(string='Leave Reference',
                         readonly=True, required=True, copy=False,
                         index=True, create=True, track_visibility="onchange", default=lambda self: _('New'))

    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_leave_rel', 'doc_id', 'attach_leave_id',
                                         string="Attachment", help='You can attach the copy of your document here ',
                                         copy=False)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('send', 'Send Request'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Department-Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'HR-Second Approval'),
        ('validate', 'CEO-Approved')],
        string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('leave_code', _('New')) == _('New'):
            vals['leave_code'] = self.env['ir.sequence'].next_by_code('leave.request') or _('New')
        result = super(AlloyLeaveCustom, self).create(vals)
        return result


    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})


    @api.multi
    def action_send(self):
        user_group = self.env.ref("alloy_leave_custom.group_department_leave_approve")
        sub = _("Leave Request / Department Approve")
        content = _(
            "Hello,<br>Mr/Mrs: <b>" + str(
                self.create_uid.name) + "</b> Has a <b>Leave</b> request  with <b>REF:</b> <b>" + (self.leave_code) + "</b> requires your approve," \
                                        "<br>May you check it please.. ")
        self._send_email_request(user_group, sub, content)
        self.write({'state': 'send'})
        self.activity_update()
        return True

    @api.multi
    #department
    def action_confirm(self):
        # if self.filtered(lambda holiday: holiday.state != 'draft'):
        #     raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
        user_group = self.env.ref("alloy_leave_custom.group_hr_leave_approve")
        sub = _("Leave Request / HR Approve")
        content = _("Hello,<br>Mr/Mrs: <b>" + str(self.create_uid.name) + "</b> Has a <b>Leave</b> request with <b>REF:</b> <b>" + (self.leave_code) + "</b> requires your approve,"\
                       "<br>May you check it please.. ")
        self._send_email_request(user_group,sub,content)
        if self.filtered(lambda holiday: holiday.state != 'send'):
            raise UserError(_('Leave request must be in send state ("Send Request") in order to confirm it.'))
        self.write({'state': 'confirm'})
        self.activity_update()
        return True

    @api.multi
    #hr
    def action_approve(self):
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))
        # current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1', 'first_approver_id': current_employee.id})
        # self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        user_group = self.env.ref("alloy_leave_custom.group_ceo_leave_approve")
        sub = _("Leave Request / CEO Approve")
        content = _(
            "Hello,<br>Mr/Mrs: <b>" + str(
                self.create_uid.name) + "</b> Has a <b>Leave</b> request  with <b>REF:</b> <b>" + (self.leave_code) + "</b> requires your approve,"
                                        "<br>May you check it please.. ")
        self._send_email_request(user_group, sub, content)
        self.write({'state': 'validate1'})
        self.activity_update()
        return True


    @api.multi
    #ceo
    def action_validate(self):
        sub = _("User Request")
        content = _("Hello,<br>Mr/Mrs: <b>" + str(self.create_uid.name) + "your request  with <b>REF:</b> <b>" + (self.leave_code) + "</b> has been approved," \
                               "<br>May you check it please.. ")
        recipient_partners = []
        # if self.env.user:
        #     recipient_partners.append(self.env.user.partner_id.id)

        recipient_partners = []
        if self.env.user:
            print(self.env.user.name)
            print (recipient_partners.append(self.env.user.partner_id.id))
            if len(recipient_partners):
                print(recipient_partners)
                self.message_post(body=content,
                                  subtype='mt_comment',
                                  subject=sub,
                                  partner_ids=recipient_partners,
                                  message_type='comment')
        self.write({'state': 'validate'})
        self.activity_update()
        return True



    @api.multi
    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # if any(holiday.state not in ['confirm', 'validate', 'validate1'] for holiday in self):
        #     raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))
        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        (self - validated_holidays).write({'state': 'refuse', 'second_approver_id': current_employee.id})
        # Delete the meeting
        self.mapped('meeting_id').unlink()
        # If a category that created several holidays, cancel all related
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_refuse()
        self.write({'state': 'refuse'})
        self._remove_resource_leave()
        self.activity_update()
        return True

    def _send_email_request(self, user_group, sub, content):
        recipient_partners = []
        for group in user_group:
            for recipient in group.users:
                if recipient.partner_id.id not in recipient_partners:
                    recipient_partners.append(recipient.partner_id.id)
                    if len(recipient_partners):
                        self.message_post(body=content,
                                          subtype='mt_comment',
                                          subject=sub,
                                          partner_ids=recipient_partners,
                                          message_type='comment')


    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        is_user = self.env.user.has_group('alloy_leave_custom.group_user')
        for holiday in self:
            val_type = holiday.holiday_status_id.validation_type
            if state == 'confirm':
                continue


            if state == 'send':
                if holiday.employee_id != current_employee and not is_user:
                    raise UserError(_('Only a Leave user can can change leave requests state to (Send Request).'))
                continue

            if state == 'draft':
                if holiday.employee_id != current_employee and not is_manager:
                    raise UserError(_('Only a Leave Manager can reset other people leaves.'))
                continue

            if not is_officer:
                raise UserError(_('Only a Leave Officer or Manager can approve or refuse leave requests.'))

            if is_officer:
                # use ir.rule based first access check: department, members, ... (see security.xml)
                holiday.check_access_rule('write')


class leave_attemcti(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_leave_rel = fields.Many2many('hr.leave', 'doc_attachment_id', 'attach_leave_id', 'doc_id',
                                            string="Attachment", invisible=1)



