# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models ,_
from odoo.exceptions import UserError


class HrLeavesInherit(models.Model):
    _inherit = 'hr.leave'
    _description = 'HR Leave'

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help="The status is set to 'To Submit', when a leave request is created." +
        "\nThe status is 'To Approve', when leave request is confirmed by user." +
        "\nThe status is 'Refused', when leave request is refused by manager." +
        "\nThe status is 'Approved', when leave request is approved by manager.")


    @api.multi
    def action_confirm(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))

        user_group = self.env.ref("hr.group_hr_manager")
        sub = _("Leave Request")
        content = _("Hello,<br>Mr/Mrs: <b>" + str(self.create_uid.name) + "</b> Has a <b>Leave</b> request requires your approve,"\
                       "<br>May you check it please.. ")
        self._send_email_request(user_group,sub,content)

        self.write({'state': 'confirm'})
        self.activity_update()
        return True


    def _send_email_request(self,user_group,sub,content):
        recipient_partners = []
        for group in user_group:
            print('asd1')
            for recipient in group.users:
                print(recipient)
                if recipient.partner_id.id not in recipient_partners:
                    recipient_partners.append(recipient.partner_id.id)

        if len(recipient_partners):
            print(recipient_partners)
            self.message_post(body=content,
                           subtype='mt_comment',
                           subject=sub,
                           partner_ids=recipient_partners,
                           message_type='comment')