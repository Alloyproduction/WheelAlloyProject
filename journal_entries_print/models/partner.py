from odoo import fields, models

class Partner(models.Model):
    _inherit = 'account.bank.statement'

    # Add a new column to the res.partner model, by default partners are not
    # instructors

    po_number = fields.Char('Next Action')

class journal_post_button(models.Model):
        _inherit = 'account.move'

        # Add a new column to the res.partner model, by default partners are not
        # instructors


