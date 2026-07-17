from odoo import models, fields


FISCAL_PROFILE_SELECTION = [
    ('standard', 'Estándar'),
    ('withholding_agent', 'Agente de retención'),
    ('exempt', 'Exento'),
]


class WithholdingRule(models.Model):
    _name = 'withholding.rule'
    _inherit = ['mail.thread']
    _order = 'fiscal_profile'
    _description = 'Regla de retención por perfil fiscal'


    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True
    )
    fiscal_profile = fields.Selection(
        FISCAL_PROFILE_SELECTION,
        string='Perfil fiscal',
        required=True,
        tracking=True
    )
    withholding_percentage = fields.Float(
        string='Porcentaje de retención',
        digits=0,
        default=0.0,
        required=True,
        tracking=True
    )

    active = fields.Boolean(
        default=True
    )

    _check_withholding_percentage = models.Constraint(
        'CHECK(withholding_percentage>=0 AND withholding_percentage<=100)',
        'El porcentaje de retención debe ser un número entre 0 y 100'
    )

    _unique_fiscal_profile = models.Constraint(
        'UNIQUE(fiscal_profile)',
        'Ya existe una regla de retención para este perfil fiscal'
    )
