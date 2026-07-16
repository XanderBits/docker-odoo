from odoo import models, fields, api


class PosDiscountRule(models.Model):
    _name = 'pos.discount.rule'
    _description = 'Regla de descuento por horario en el punto de venta'

