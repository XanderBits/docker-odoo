from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for rec in orders: 
            discount_rule = (
                self.env['pos.discount.rule']
                ._get_discount_rule_by_hour_range(rec.date_order)
            )
            if not discount_rule:
                _logger.info("POS ORDER CREATE: NO SE APLICARON REGLAS DE DESCUENTO")
                continue
            
            for line in rec.lines:
                line.discount = max(
                    line.discount, 
                    discount_rule.discount_percentage
                )
                amounts = line._compute_amount_line_all()
                line.price_subtotal_incl = amounts['price_subtotal_incl']
                line.price_subtotal = amounts['price_subtotal']
            
            _logger.info(f"POS ORDER CREATE: DESCUENTO APLICADO A ORDEN {rec.id}")
        
        return orders
