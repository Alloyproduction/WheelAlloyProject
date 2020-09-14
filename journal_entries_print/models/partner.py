from odoo import fields, models


class Partner(models.Model):
    _name = "account.partner"
    _inherit = ['account.bank.statement', 'purchase.order', 'mail.thread', 'mail.activity.mixin']

    # po_number = fields.Char('Next Action')
    po_number = fields.Many2one('purchase.order',
                                ondelete='set null', string="PO Number", index=True)
    _CLAIMSTATES = [
        ('stat_draft', 'Draft'),
        ('stat_confirmed', 'Confirmed'),
        ('stat_process', 'process'),
        ('stat_won', 'won'),
        ('stat_lost', 'lost'),
    ]

    state = fields.Selection(selection=_CLAIMSTATES)





@api.multi
def action_draft(self):
    self.state = 'stat_draft'
    return self.write({'state': 'stat_draft'})
    self.ldate = datetime.now()


@api.multi
def action_confirm(self):
    res = super(Partner, self).action_confirm()
    res_conf = self.env['res.config.settings'].sudo()
    self.state = 'stat_confirmed'
    return self.write({'state': 'stat_confirmed'})
    self.ldate = datetime.now()


@api.multi
def action_process(self):
    res = super(Partner, self).action_process()
    res_conf = self.env['res.config.settings'].sudo()
    self.state = 'stat_process'
    return self.write({'state': 'stat_process'})
    self.ldate = datetime.now()


class journal_post_button(models.Model):
        _inherit = 'account.move'

