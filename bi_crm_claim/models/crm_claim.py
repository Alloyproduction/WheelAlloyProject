# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp
#############################################################################################################################################


_CLAIMSTATES = [
    ('stat_draft', 'Draft'),
    ('stat_confirmed', 'Confirmed'),
    ('stat_process', 'process'),
    ('stat_won', 'won'),
    ('stat_lost', 'lost'),
]



class crm_claim_stage(models.Model):
    _name = "crm.claim.stage"
    _description = "Claim stages"
    _rec_name = 'name'
    _order = "sequence"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.",default=lambda *args: 1)
    team_ids = fields.Many2many('crm.team', 'crm_team_claim_stage_rel', 'stage_id', 'team_id', string='Teams',
                        help="Link between stages and sales teams. When set, this limitate the current stage to the selected sales teams.")
    case_default = fields.Boolean('Common to All Teams',
                        help="If you check this field, this stage will be proposed by default on each sales team. It will not assign this stage to existing teams.")


    _defaults = {
        'sequence': lambda *args: 1
    }



class crm_claim(models.Model):
    _name = "crm.claim"
    _description = "Claim"
    _order = "priority,date desc"
    _inherit = ['mail.thread']

    ##################################################################################################################
    @api.onchange('type_action')
    def get_action_type(self):
        for rec in self:
            if rec.type_action:
                rec.addition_deit = rec.type_action.resolution
 ############################################################################################3

    @api.multi
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        team_id = self.env['crm.team'].sudo()._get_default_team_id()
        return self._stage_find(team_id=team_id.id, domain=[('sequence', '=', '1')])

    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('crm.claim')

    id = fields.Integer('ID', readonly=True)
    code = fields.Char('Code', size=32, required=True, default=_get_default_name, track_visibility='onchange')
    # states = {'draft': [('readonly', False)]},
    name = fields.Char('Claim Subject', required=True)
    active = fields.Boolean('Active',default=lambda *a: 1)
    action_next = fields.Char('Next Action')
    date_action_next = fields.Datetime('Next Action Date')
    description = fields.Text('Description')
    create_date = fields.Datetime('Creation Date' , readonly=True)
    write_date = fields.Datetime('Update Date' , readonly=True)
    date_deadline = fields.Datetime('Deadline')
    date_closed = fields.Datetime('Closed', readonly=True)
    date = fields.Datetime('Claim Date', select=True,default=lambda self: self._context.get('date', fields.Datetime.now()))
    categ_id = fields.Many2one('crm.claim.category', 'Category')
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority',default='1')
    type_action = fields.Many2one('crm.claim.category', 'Action Type')
    # resolution = fields.Many2one('action.claim', 'resolution')
    addition_deit = fields.Text('Additional details')
    # resolution1 = fields.Selection([('1', 'Corrective Action'), ('2', 'Preventive Action')], 'Resolution1')
    user_id = fields.Many2one('res.users', 'Responsible',  track_visibility = 'always', default=_default_user)
    user_fault = fields.Char('Trouble Responsible')
    team_id = fields.Many2one('crm.team', 'Sales Team', oldname='section_id', \
                              select=True, help="Responsible sales team." \
                                                " Define Responsible user and Email account for" \
                                                " mail gateway.")  # ,default=lambda self: self.env['crm.team']._get_default_team_id()
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env['res.company']._company_default_get('crm.case'))
    partner_id = fields.Many2one('res.partner', 'Partner')
    sale_id = fields.Many2one('sale.order', 'Sales Order')
    email_cc = fields.Text('Watchers Emails', size=252, help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    email_from = fields.Char(related="partner_id.email", string= 'Email', size=128, help="Destination email for email gateway.")
    partner_phone = fields.Char(related="partner_id.mobile", string="Phone")
    stage_id = fields.Many2one ('crm.claim.stage', 'Stage', track_visibility='onchange',
                domain="['|', ('team_ids', '=', team_id), ('case_default', '=', True)]")    #,default=lambda self:self.env['crm.claim']._get_default_stage_id()
    cause = fields.Text('Root Cause')
#################################################################################################################################################################
             # stage + workflow code

    ldate = fields.Datetime(string = 'Update Stage Date')
    state = fields.Selection(selection=_CLAIMSTATES,
                             string='Status',
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='stat_draft')
############################################################################################################################
    # @api.model
    # def create(self, vals):
    #     if vals.get('code', _('New')) == _('New'):
    #             vals['code'] = self.env['ir.sequence'].next_by_code('crm.claim') or _('New')
    #     result = super(crm_claim, self).create(vals)
    #     return result



###########################################################################################################################


###################################################################################################
    @api.multi
    def action_draft(self):
        # self.state = 'stat_draft'
        return self.write({'state': 'stat_draft'})
        self.ldate = datetime.now()

    @api.multi
    def action_confirm(self):
        # self.state = 'stat_confirmed'
        return self.write({'state': 'stat_confirmed'})
        self.ldate = datetime.now()

    @api.multi
    def action_process(self):
        # self.state = 'stat_process'
        return self.write({'state': 'stat_process'})
        self.ldate = datetime.now()

    @api.multi
    def action_won(self):
        # self.state = 'stat_won'
        return self.write({'state': 'stat_won'})
        self.ldate = datetime.now()

    @api.multi
    def action_lost(self):
        # self.state1 = 'stat_lost'
        return self.write({'state': 'stat_lost'})
        self.ldate = datetime.now()

#############################################################################################################################################
     #stage group by search

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['claim.stages'].search([])
        return stage_ids

    claim_stage = fields.Many2one(comodel_name="claim.stages", string="Claim stages",
                                  group_expand='_read_group_stage_ids')

#############################################################################################################################################
    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self, email=False):
        if not self.partner_id:
            return {'value': {'email_from': False, 'partner_phone': False}}
        address = self.pool.get('res.partner').browse(self.partner_id)
        return {'value': {'email_from': address.email, 'partner_phone': address.phone}}

    @api.model
    def create(self, vals):
        context = dict(self._context or {})
        if vals.get('team_id') and not self._context.get('default_team_id'):
            context['default_team_id'] = vals.get('team_id')

        # context: no_log, because subtype already handle this
        return super(crm_claim, self).create(vals)

    @api.multi
    def message_new(self,msg, custom_values=None):
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(crm_claim, self).message_new(msg, custom_values=defaults)
    # all_crm_claim = fields.Text(string ="All Crm claim " , compute='get_crm_info()')

    @api.model
    def get_confirm_state_info(self):
        uid = self.env.user.id
        tot_won = self.env['crm.claim'].search([('user_id', '=', uid),('state', '=', 'stat_won')])
        for r in tot_won:
            print(r)

        print(len(tot_won))
        return {"won": "%s"%(len(tot_won))}


    @api.model
    def get_crm_info(self):
        uid = self.env.user.id
        cr = self.env.cr
        user_id = self.env['res.users'].browse(uid)
        # today_date = datetime.datetime.now().date()
        my_pipeline = self.env['crm.claim'].sudo().search_count([('user_id', '=', uid)])
        tot_won = self.env['crm.claim'].sudo().search_count([('user_id', '=', uid), ('state', '=', 'stat_won')])
        tot_lost = self.env['crm.claim'].sudo().search_count([('user_id', '=', uid), ('state', '=', 'stat_lost')])
        tot_process = self.env['crm.claim'].sudo().search_count([('user_id', '=', uid), ('state', '=', 'stat_process')])
        tot_confirm = self.env['crm.claim'].sudo().search_count(
            [('user_id', '=', uid), ('state', '=', 'stat_confirmed')])
        tot_draft = self.env['crm.claim'].sudo().search_count([('user_id', '=', uid), ('state', '=', 'stat_draft')])

        # tot_overdue_opportunities = self.env['crm.claim'].sudo().search_count(
        #     [('type', '=', 'opportunity'), ('date_deadline', '<', today_date), ('date_closed', '=', False)])
        # tot_open_opportunities = self.env['crm.lead'].sudo().search_count(
        #     [('type', '=', 'opportunity'), ('probability', '<', 100)])

        # tot_won = self.env['crm.claim'].sudo().search_count([('active', '=', True), ('state', '=', 'won')])
        # tot_lost = self.env['crm.lead'].sudo().search_count([('active', '=', False), ('probability', '=', 0)])
        # crm_details = self.env['crm.lead'].sudo().search_read([('user_id', '=', uid)], limit=1)
        # crm_details = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)

        crm_search_view_id = self.env.ref('bi_crm_claim.claim_search_view')
        # timesheet_search_view_id = self.env.ref('hr_timesheet.hr_timesheet_line_search')
        # job_search_view_id = self.env.ref('hr_recruitment.view_crm_case_jobs_filter')
        # attendance_search_view_id = self.env.ref('hr_attendance.hr_attendance_view_filter')
        # expense_search_view_id = self.env.ref('hr_expense.view_hr_expense_sheet_filter')

        # leaves_to_approve = self.env['hr.leave'].sudo().search_count([('state', 'in', ['confirm', 'validate1'])])
        # leaves_alloc_to_approve = self.env['hr.leave.allocation'].sudo().search_count([('state', 'in', ['confirm', 'validate1'])])
        # timesheets = self.env['account.analytic.line'].sudo().search_count(
        #     [('project_id', '!=', False), ])
        # timesheets_self = self.env['account.analytic.line'].sudo().search_count(
        #     [('project_id', '!=', False), ('user_id', '=', uid)])
        # job_applications = self.env['hr.applicant'].sudo().search_count([])
        # attendance_today = self.env['hr.attendance'].sudo().search_count([('check_in', '>=',
        #                     str(datetime.datetime.now().replace(hour=0, minute=0, second=0))),
        #                     ('check_in', '<=', str(datetime.datetime.now().replace(hour=23, minute=59, second=59)))])
        # expenses_to_approve = self.env['hr.expense.sheet'].sudo().search_count([('state', 'in', ['submit'])])

        # obj_opr = self.env['crm.lead'].sudo().search([])
        # expected_revenue = 0
        # for lead in obj_opr:
        #     expected_revenue = round(expected_revenue + (lead.planned_revenue or 0.0) * (lead.probability or 0) / 100.0,
        #                              2)
        #     # payroll Datas for Bar chart
        # query = """
        #          select state,count(state) from crm.claim where user_id =
        #
        #       """ + str(uid)
        # cr.execute(query)
        # crm_details = cr.dictfetchall()


        crm_details = [{}]
        if crm_details:
            # categories = self.env['hr.employee.category'].sudo().search([('id', 'in', crm_details[0]['category_ids'])])
            data = {
                'my_pipe_line': my_pipeline,
                'tot_confirm': tot_confirm,
                'tot_draft': tot_draft,
                'tot_won': tot_won,
                'tot_lost': tot_lost,
                'tot_process': tot_process,
                'user_id': user_id.id,
                'graph_exp_revenue_label': ['New','Confirm','Process','Won','Lost'],
                'graph_exp_revenue_dataset': [tot_draft,tot_confirm,tot_process,tot_won,tot_lost],

            }

            crm_details[0].update(data)

            print("CRM________________", crm_details)
        return crm_details



class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _claim_count(self):
        for claim in self:
            claim_ids = self.env['crm.claim'].search([('partner_id','=',claim.id)])
            claim.claim_count = len(claim_ids)


    claim_count = fields.Float(string="claim count", compute="_claim_count")

    @api.multi
    def claim_button(self):
        self.ensure_one()
        return {
            'name': 'Partner Claim',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'crm.claim',
            'domain': [('partner_id', '=', self.id)],
        }

class crm_claim_category(models.Model):
    _name = "crm.claim.category"
    _description = "Category of claim"

    name = fields.Char('Name', required=True, translate=True)
    team_id = fields.Many2one('crm.team', 'Sales Team')
    type_action = fields.Char(string = 'Action Type')
    resolution = fields.Char(string='Resolution')


class UtmCampaign(models.Model):
    # OLD crm.case.resource.type
    _name = 'utm.campaign1'
    _description = 'UTM Campaign'

    name = fields.Char(string='Campaign Name', required=True, translate=True)




# class crm_claim(models.Model):
#     _name = "action.claim"
#     _description = "Claim"

    # type_action = fields.Char(string = 'Action Type')
    # # type_action = fields.Selection([('correction','Corrective Action'),('prevention','Preventive Action')], 'Action Type')
    # resolution = fields.Selection([('1','Corrective Action'),('2','Preventive Action')], 'Action Type')
    #
    # @api.onchange('type_action')
    # def get_action_type(self):
    #     for rec in self:
    #         if rec.type_action:
    #             rec.addition_deit = rec.type_action.resolution


