from odoo import models, fields

from odoo.addons.fiscal_profile_withholding.models.withholding_rule import (
    FISCAL_PROFILE_SELECTION,
)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fiscal_profile = fields.Selection(
        FISCAL_PROFILE_SELECTION,
        string='Perfil fiscal',
        tracking=True,
        help=("El perfil fiscal determinará como se "
            "aplicarán retenciones automáticas en facturas"
        )
    )
