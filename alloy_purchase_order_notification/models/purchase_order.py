# -*- coding: utf-8 -*-

from odoo import models, api,_


class SprogrouppurcaseRequest(models.Model):
    _inherit = "sprogroup.purchase.request"

    @api.multi
    def button_to_approve(self):
        res = super(SprogrouppurcaseRequest, self).button_to_approve()

        ###########
        # mo. edit
        ###########
        msg_body = "<b>New purchase request require your approval</b>" + "<br><b>Request Name:</b> " + str(
            self.name) + " / " + str(self.code) \
                   + "<b><br>Requested By:</b> " + str(self.requested_by.name) \
                   + "<b><br>Employee Name: </b>" + str(self.employee_name.name) \
                   + "<b><br>Vendor: </b>" + str(self.partner_id.name) \
                   + "<b><br>Department: </b>" + str(self.department_id.name) \
                   + "<b><br>Start/End Date: </b>" + str(self.date_start) + " : " + str(self.end_start)

        activities = {}
        list = []
        task_description = ""
        # total = 0
        for i in self.line_ids:
            # total += i.product_qty
            activities.update(
                {'Product': i.product_id.name, 'Description': i.name,
                 'Quantity': i.product_qty, 'Request Date': i.date_required})
            list.append(activities)
            task_description += "<tr>   <td  align=""center""> <font size=""2"">{3}</font></td>" \
                                "<td  align=""center""> <font size=""2"">{2}</font></td>" \
                                "<td  align=""center""> <font size=""2"">{1}</font></td>    " \
                                "<td  align=""center""> <font size=""2"">{0}</font></td>  </tr>" \
                .format(str(i.date_required), str(i.product_qty), str(i.name), str(i.product_id.name), )

            print(task_description)

            status_table = " <font size=""2"">   <p> {0}<br>---------------------------- </p>" \
                           "<table style=""width:80%"" border="" 1px solid black"">" \
                           "<tr> <th><font size=""2"">Product</font> </th>    " \
                           "<th><font size=""2"">Description</font> </th>    " \
                           "<th><font size=""2"">Quantity</font> </th>    " \
                           "<th><font size=""2"">Request Date</font> </th>    </tr>{1}" \
                           "</table>" \
                           "<p> <p>Regards,</p> </font>" \
                .format(msg_body, task_description, i.date_required, i.product_qty, i.name, i.product_id.name)
            print(status_table)

        msg_sub = self.name + "/" + self.code \
                  + " / " + self.requested_by.name + " / " + self.state
        ###########
        # mo. edit
        ###########

        for rec in self:
            msg_body = "New purchase request require your approval" + status_table

            msg_sub = "Approve Purchase Request" + " / " + msg_sub
            groups = self.env['res.groups'].search([('name', '=', 'Sprogroup Purchase Request Manager')])
            recipient_partners = []
            for group in groups:
                for recipient in group.users:
                    if recipient.partner_id.id not in recipient_partners:
                        recipient_partners.append(recipient.partner_id.id)
            if len(recipient_partners):
                rec.message_post(body=msg_body,
                                 subtype='mt_comment',
                                 subject=msg_sub,
                                 partner_ids=recipient_partners,
                                 message_type='comment')
        return res