
from odoo import models, fields, api, _
from datetime import datetime

class Wizard2(models.TransientModel):
    _name = 'salesman.wizard2'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "sales_man"

    sales_man = fields.Many2one('res.users',string="Sales Man")

    def send_msg(self):
        date_deadline = datetime.now().strftime('%Y-%m-%d')
        user_id = self.sales_man
        msubj = "Check This Activity"
        mbody = "..."
        x = self.env['crm.claim'].browse(self._context.get('active_id'))

        print(x)

        model_id = self.env['ir.model']._get('crm.claim').id
        act_type_xmlid = 'mail.mail_activity_data_todo'
        if act_type_xmlid:
            print("True")
            activity_type = self.sudo().env.ref(act_type_xmlid)
        create_vals = {
            'activity_type_id': activity_type.id,
            'summary': msubj or activity_type.summary,
            'automated': True,
            'note': mbody,
            'date_deadline': date_deadline,
            'res_model_id': model_id,
            'res_id': x.id,
            'user_id': user_id.id,
        }
        print(create_vals)

        self.env['mail.activity'].sudo().create(create_vals)

        # if user_id:
        #     self.sudo().activity_schedule(
        #         'mail.mail_activity_data_todo', date_deadline,
        #         note=mbody,
        #         user_id=user_id,
        #         res_id=x,
        #         summary=msubj
        #     )

        # self.sudo().message_post(body=mbody,
        #                       subtype='mt_comment',
        #                       subject=msubj,
        #                       partner_ids=user_email,
        #                       message_type='comment')
