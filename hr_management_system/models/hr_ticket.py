# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime

class HRTicket(models.Model):
    _name = 'hr.ticket'
    _description = 'Employees Tickets'
    _inherit = ['mail.thread','mail.activity.mixin']

    # dt = Department
    # emp = Employee

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    ticket_name = fields.Many2one('ticket.type', string="Ticket Type")
    ticket_claim = fields.Float('Ticket Entitlement')
    emp_id = fields.Many2one('hr.employee', required=True, string="Employee")
    emp_job_id = fields.Many2one('hr.job', compute="_compute_employee", store=True, readonly=True, string="Job Position")

    doc_attachment_id08 = fields.Many2many('ir.attachment', 'doc_attach_rel08', 'doc_id08','attach_id08', string="Attachment", copy=False)

    date_from = fields.Date("Date From", default=fields.Date.today())
    date_to = fields.Date("Date To")
    description = fields.Text('Description')
    state = fields.Selection([('draft','Draft'),
                              ('request','Request'),
                              ('man_approve','Manager Approve'),
                              ('approve','Approved'),
                              ('reject','Rejected'),],
                              default='draft')

    @api.model
    def create(self, vals):
        # assigning the sequence for the record
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.ticket') or _('New')
        res = super(HRTicket, self).create(vals)
        return res

    @api.depends('emp_id')
    def _compute_employee(self):
        for i in self.filtered('emp_id'):
            i.emp_job_id = i.emp_id.job_id


    # def make_activity(self, user_ids):
    #     print("j...", user_ids)
    #     now = datetime.now()
    #     date_deadline = now.date()
    #
    #     if self:
    #         if user_ids:
    #             actv_id = self.sudo().activity_schedule(
    #                 'mail.mail_activity_data_todo', date_deadline,
    #                 note=_(
    #                     '<a href="#" data-oe-model="%s" data-oe-id="%s">Task </a> for <a href="#" data-oe-model="%s" data-oe-id="%s">%s\'s</a> Review') % (
    #                          self._name, self.id, self.emp_id._name,
    #                          self.emp_id.id, self.emp_id.display_name),
    #                 user_id=user_ids,
    #                 res_id=self.id,
    #
    #                 summary=_("Request Approve")
    #             )
    #             print("active", actv_id)

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

    @api.multi
    def emp_request_action(self):

        user_group = self.env.ref("hr_management_system.group_hr_manager_demo")
        sub = _("Employee Ticket Request - HrManager")
        content = _("Hello,<br>Mr/Mrs: <b>" + str(self.emp_id.name) + "</b> Has a <b>Ticket</b> request requires your approve,"\
                       "<br>May you check it please.. ")

        self._send_email_request(user_group,sub,content)

        return self.write({'state': 'request'})

    @api.multi
    def hr_manager_action(self):

        return self.write({'state': 'man_approve'})

    @api.multi
    def hr_administrator_action(self):

        user_group = self.env.ref("hr.group_hr_manager")
        sub = _("Employee Ticket Request - HrAdmin")
        content = _("Hello,<br>Mr/Mrs: <b>" + str(self.emp_id.name) + "</b> Has a <b>Ticket</b> request requires your approve,"\
                       "<br>May you check it please.. ")

        self._send_email_request(user_group,sub,content)

        return self.write({'state': 'approve'})

    @api.multi
    def reject_action(self):
        return self.write({'state': 'reject'})

    @api.multi
    def reset_action(self):
        return self.write({'state': 'draft'})


class HRTicketType(models.Model):
    _name = 'ticket.type'

    name = fields.Char("Name")


class HrTicketAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel08 = fields.Many2many('hr.ticket', 'doc_attachment_id08', 'attach_id08', 'doc_id08',
                                        string="Attachment", invisible=1)

