from odoo import models, fields, api, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    REPLENISHMENT_PRIORITY_SELECTION = [
        ('high', 'Alta'),
        ('medium', 'Media'),
        ('low', 'Baja'),
        ('none', 'Sin prioridad'),
    ]

    replenishment_priority = fields.Selection(
        REPLENISHMENT_PRIORITY_SELECTION, 
        string='Prioridad de Reabastecimiento',
        default='none'
    )

    target_stock = fields.Integer(
        string='Stock Objetivo',
    )

    needs_replenishment = fields.Boolean(
        string='¿Requiere reabastecimiento?',
        compute='_compute_product_needs_replenishment',
        search='_search_needs_replenishment',
    )

    @api.depends('qty_available', 'target_stock')
    def _compute_product_needs_replenishment(self):
        for rec in self:
            rec.needs_replenishment = rec.qty_available < rec.target_stock

    def _search_needs_replenishment(self, operator, value):
        products = self.search([])
        matching = products.filtered_domain([
                ('needs_replenishment', operator, value)
        ])
        return [('id', 'in', matching.ids)]

    def _cron_check_target_stock(self):
        product_ids = self.search([('needs_replenishment', '!=', False)])
        if not product_ids:
            _logger.info("CHECK PRODUCT TARGET STOCK: No se encontraron productos")
            return
        
        activity_type_id = self.env.ref((
                'priority_replenishment_rules'
                '.mail_activity_product_replenishment'
        )).id
        res_model_id = self.env.ref('product.model_product_template').id

        for product in product_ids:
            existing_activity = self.env['mail.activity'].search([
                ('res_id', '=', product.id),
                ('res_model_id', '=', res_model_id ),
                ('activity_type_id', '=', activity_type_id)
            ], limit=1)
            
            if existing_activity:
                _logger.info((
                    f"NO SE CREÓ LA ACTIVIDAD: "
                    f"YA EXISTE UNA PARA EL PRODUCTO '{product.name}': "
                    f"{existing_activity}"
                ))
                continue

            note = self._get_replenishment_activity_note(product)
            activity = product.sudo().activity_schedule(
                'priority_replenishment_rules.mail_activity_product_replenishment',
                note=note,
                user_id=product.responsible_id.id or SUPERUSER_ID,
                date_deadline=self._get_priority_date_to_overdue(
                    product.replenishment_priority
                )
            )
            _logger.info(f"CHECK PRODUCT TARGET STOCK: Actividad creada {activity}")

    def _get_replenishment_activity_note(self, product):
        priority = (
            dict(self._fields['replenishment_priority'].selection)
            .get(product.replenishment_priority, "")
            .upper()
        ) or "SIN PRIORIDAD"
        note = (
            "REGLA DE REABASTECIMIENTO: Se necesita reabastecer "
            f"el producto {product.name} que tiene "
            f"una prioridad '{priority}'. "
            "Por favor, tomar las medidas necesarias."
        )

        return note

    def _get_priority_date_to_overdue(self, product_priority):
        priority_days = {'high': 1, 'medium': 4, 'low': 8}
        date_deadline = (
            fields.Date.context_today(self) 
            + relativedelta(days=priority_days.get(product_priority, 4))
        )
        return date_deadline