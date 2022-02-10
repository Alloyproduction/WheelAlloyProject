# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class alloyleave(models.Model):
    _name = "hr.leave"
    _inherit = "hr.leave"


    leave_code = fields.Char(string='Leave Reference',
                         readonly=True, required=True, copy=False,
                         index=True, create=True, track_visibility="onchange", default=lambda self: _('New'))

    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_leave_rel', 'doc_id', 'attach_leave_id', string="Attachment",
                                         help='You can attach the copy of your document here ', copy=False)


    state = fields.Selection(selection_add=[
                                               ("send", "Send"),
                                               ('draft', 'TO Submit'), ('cancel', 'Cancelled'),
                                               ('refuse', 'Refused'),
                                               ('send', 'Send'),
                                               ('confirm', 'To Approve'),
                                               ('validate1', 'second Approval'), ('validate', 'Approved')])





    @api.model
    def create(self, vals):
        if vals.get('leave_code', _('New')) == _('New'):
            vals['leave_code'] = self.env['ir.sequence'].next_by_code('leave.request') or _('New')
        result = super(alloyleave, self).create(vals)
        return result

    @api.multi
    def action_confirm(self):
        # if self.filtered(lambda holiday: holiday.state != 'draft'):
        #     raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))

        user_group = self.env.ref("alloy_leave_custom.group_hr_leave_approve")
        sub = _("Leave Request")
        content = _("Hello,<br>Mr/Mrs: <b>" + str(self.create_uid.name) + "</b> Has a <b>Leave</b> request requires your approve,"\
                       "<br>May you check it please.. ")
        self._send_email_request(user_group,sub,content)

        self.write({'state': 'confirm'})
        self.activity_update()
        return True


        # msg_body = " Request by... " + "" + self.env.user.name
        # msg_sub = "Audit Petty Cash [" + self.leave_code + "]"
        #
        # groups = self.env['res.groups'].search([('name', '=', 'HR Approve')])
        # recipient_partners = []
        # for group in groups:
        #     for recipient in group.users:
        #         if recipient.partner_id.id not in recipient_partners:
        #             recipient_partners.append(self.recipient.partner_id.id)
        # if len(recipient_partners):
        #     self.message_post(body=msg_body,
        #                       subtype='mt_comment',
        #                       subject=msg_sub,
        #                       partner_ids=recipient_partners,
        #                       message_type='comment')
        # return self.write({'state': 'confirm'})



    @api.multi
    def action_validate(self):
        user_group = self.env.ref("alloy_leave_custom.group_ceo_leave_approve")
        sub = _("Leave Request")
        content = _("Hello,<br>Mr/Mrs: <b>" + str(self.create_uid.name) + "</b> Has a <b>Leave</b> request requires your approve,"\
                       "<br>May you check it please.. ")
        self._send_email_request(user_group,sub,content)

        self.write({'state': 'validate1'})
        self.activity_update()
        return True


    @api.multi
    def action_approve(self):
        # user_group = self.env.ref("alloy_leave_custom.group_department_leave_approve")
        # sub = _("Leave Request")
        # content = _(
        #     "Hello,<br>Mr/Mrs: <b>" + str(
        #         self.create_uid.name) + "</b> Has a <b>Leave</b> request requires your approve," \
        #                                 "<br>May you check it please.. ")
        # self._send_email_request(user_group, sub, content)

        self.write({'state': 'validate'})
        self.activity_update()
        return True


    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def action_refuse(self):
        # user_group = self.env.ref("alloy_leave_custom.group_department_leave_approve")
        # sub = _("Leave Request")
        # content = _(
        #     "Hello,<br>Mr/Mrs: <b>" + str(
        #         self.create_uid.name) + "</b> Has a <b>Leave</b> request requires your approve," \
        #                                 "<br>May you check it please.. ")
        # self._send_email_request(user_group, sub, content)

        self.write({'state': 'refuse'})
        self.activity_update()
        return True

        # return self.write({'state': 'refuse'})


    @api.multi
    def action_send(self):
        user_group = self.env.ref("alloy_leave_custom.group_department_leave_approve")
        sub = _("Leave Request")
        content = _(
            "Hello,<br>Mr/Mrs: <b>" + str(
                self.create_uid.name) + "</b> Has a <b>Leave</b> request requires your approve," \
                                        "<br>May you check it please.. ")
        self._send_email_request(user_group, sub, content)

        self.write({'state': 'send'})
        self.activity_update()
        return True

        # return self.write({'state': 'send'})




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


class leave_attemcti(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_leave_rel = fields.Many2many('hr.leave', 'doc_attachment_id', 'attach_leave_id', 'doc_id',
                                            string="Attachment", invisible=1)



