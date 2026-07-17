from odoo import models, fields, api


class PosDiscountRule(models.Model):
    _name = 'pos.discount.rule'
    _order = 'hour_from'
    _description = 'Regla de descuento por horario en el punto de venta'


    name = fields.Char(
        string='Nombre',
        required=True
    )
    hour_from = fields.Float(
        string='Hora de inicio',
        default=0, 
        required=True,
        index=True
    )
    hour_to = fields.Float(
        string='Hora de fin', 
        default=0, 
        required=True
    )
    
    discount_percentage = fields.Float(
        string='Porcentaje de descuento', 
        digits=0, 
        default=0.0,
        required=True
    )

    _check_hour_from_hour_to = models.Constraint(
        'CHECK(hour_from<hour_to)',
        'La hora de inicio debe ser menor a la hora de fin'
    )

    _check_discount_percentage = models.Constraint(
        'CHECK(discount_percentage>=0 AND discount_percentage<=100)',
        'El porcentaje de descuento debe ser un número entre 0 y 100'
    )

