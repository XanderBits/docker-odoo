from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    withholding_amount = fields.Monetary(
        string='Monto de retención',
        currency_field='currency_id',
        readonly=True
    )

    def _post(self, soft=True):
        moves = super()._post(soft=soft)
        for move in moves:
            if move.move_type == 'out_invoice':
                profile = move.partner_id.fiscal_profile
                if not profile:
                    move.withholding_amount = 0
                    continue

                withholding_rule = (
                    self.env['withholding.rule']
                    .search([('fiscal_profile', '=', profile)], limit=1)
                )
                if not withholding_rule:
                    move.withholding_amount = 0
                    continue
                
                percent = withholding_rule.withholding_percentage
                move.withholding_amount = move.amount_untaxed * percent / 100
        return moves