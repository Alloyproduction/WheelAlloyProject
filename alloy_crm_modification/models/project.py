from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = "project.task"


    @api.onchange('stage_id')
    def get_delivery_stage2(self):
        print("hi..>>..??..??")
        recipient_partners=[]
        for record in self:
            sales_id =self.env['sale.order'].search([('id', '=', record.sale)])
            if sales_id:
                print( sales_id.sales_user_id.partner_id.id)
                print(sales_id)
                recipient_partners.append(sales_id.sales_user_id.partner_id.id)
                if record.stage_id.name == 'Delivery':
                    sales_id.message_post(body="The Tasks are in Delivery Stages",
                                 subtype='mail.mt_comment',
                                 subject="The Tasks are in delivery stages of [  " + str(self.name)+" ]",
                                 partner_ids=recipient_partners,
                                 message_type='comment')




#
# class InheritSale(models.Model):
#     _inherit = 'sale.order'
#
#
#     is_task_delivered_send = fields.Boolean(compute='get_delivered_task_send', default=False)
#     send_onetime =fields.Boolean(string="sendonetime", default=False)
#
#
#     # full_url=fields.char('full_url',default="")
#
#     def get_delivered_task_send(self):
#         print("hi===????====???")
#         recipient_partners=[]
#         c=0
#         for rec in self:
#             recipient_partners.append(rec.sales_user_id.partner_id.id)
#             task_ids = self.env['project.task'].search([('sale', '=', rec.id)])
#             if task_ids:
#                 for line in task_ids:
#                     if line.stage_id.name == 'Delivery':  # line.stage_id.name == 'Finished and QC' or
#                         c+=1
#                 if(c==len(task_ids) and rec.send_onetime ==False):
#                     rec.is_task_delivered_send = True
#
#                     rec.message_post(body="The Tasks are in Delivery Stages",
#                                  subtype='mail.mt_comment',
#                                  subject="The Tasks are in delivery stages of " + str(rec.name),
#                                  partner_ids=recipient_partners,
#                                  message_type='comment')
#                     rec.send_onetime=True
#                     rec.write({'send_onetime':True,})
#
#


