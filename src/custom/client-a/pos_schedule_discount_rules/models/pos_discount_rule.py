from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PosDiscountRule(models.Model):
    _name = 'pos.discount.rule'
    _inherit= ['mail.thread']
    _order = 'hour_from'
    _description = 'Regla de descuento por horario en el punto de venta'


    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True
    )
    hour_from = fields.Float(
        string='Hora de inicio',
        default=0, 
        required=True,
        index=True,
        tracking=True
    )
    hour_to = fields.Float(
        string='Hora de fin', 
        default=0, 
        required=True,
        tracking=True
    )
    
    discount_percentage = fields.Float(
        string='Porcentaje de descuento', 
        digits=0, 
        default=0.0,
        required=True,
        tracking=True
    )

    active = fields.Boolean(
        default=True
    )

    _check_hour_from_hour_to = models.Constraint(
        'CHECK(hour_from<hour_to)',
        'La hora de inicio debe ser menor a la hora de fin'
    )

    _check_discount_percentage = models.Constraint(
        'CHECK(discount_percentage>=0 AND discount_percentage<=100)',
        'El porcentaje de descuento debe ser un número entre 0 y 100'
    )


    @api.constrains('hour_from', 'hour_to')
    def _check_overlap(self):
        for rec in self:
            # Existe una referencia visual de este constrains en 
            # el readme, por favor leerlo si es necesario.
            # (client-a/pos_schedule_discount_rules/readme.md)
            overlap_exists = self.with_context(active_test=False).search([
                ('id', '!=', rec.id),
                ('hour_to','>', rec.hour_from),
                ('hour_from','<', rec.hour_to),
            ], limit=1)

            if overlap_exists:
                active = (
                    ". (Este registro se encuentra archivado)." 
                    if not overlap_exists.active 
                    else "."
                )
                raise ValidationError((
                    "Error: Este rango de horas se solapa "
                    "con un registro existente: "
                    f"{overlap_exists.name}{active}"
                ))


    def _get_discount_rule_by_hour_range(self, date):
        date = fields.Datetime.context_timestamp(self, date)
        hour = float(date.hour + (date.minute / 60))
        discount_rule = self.search([
                ('hour_from', '<=', hour),
                ('hour_to', '>', hour),
        ], limit=1)
        return discount_rule

