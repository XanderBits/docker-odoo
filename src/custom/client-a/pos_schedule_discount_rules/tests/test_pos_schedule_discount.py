from odoo.tests import tagged
from odoo.addons.point_of_sale.tests.common import TestPoSCommon
from odoo.exceptions import ValidationError
from psycopg2.errors import CheckViolation
from odoo.tools import mute_logger
import logging

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestPosScheduleDiscount(TestPoSCommon):
    """Valida órdenes con y sin descuento por horario, incluyendo casos límite
    (orden fuera del rango horario, reglas solapadas)."""

    def setUp(self):
        super().setUp()
        self.env.user.tz = 'America/Caracas' #UTC -4
        self.config = self.basic_config
        self.categ = self.categ_basic
        self.tax = self.taxes['tax10'].ids
        self.PosDiscountRule = self.env['pos.discount.rule']
        self.PosOrder = self.env['pos.order']
        self.discount_14_16 = self.PosDiscountRule.create({
            'name': "Descuento 14-16",
            'hour_from': 14.0,
            'hour_to': 16.0,
            'discount_percentage': 20,
        })
        self.product1 = self.create_product(
            'Product 1', 
            self.categ, 
            100, 
            50, 
            self.tax
        )
        self.product2 = self.create_product(
            'Product 2', 
            self.categ, 
            100, 
            50, 
            self.tax
        )
    
    def test_order_within_schedule_gets_discount(self):
        session_id = self.open_new_session(opening_cash=0)        
        # Línea 1: 100 - 10% = 90 -> tras la regla: 100 - 20% = 80 (la regla eleva)
        # Línea 2: 100 - 30% = 70 -> tras la regla: 100 - 30% = 70 (se respeta el manual)
        order = self.PosOrder.create({
            'company_id': self.env.company.id,
            'session_id': session_id.id,
            'partner_id': False,
            'lines': [
                (0, 0, {
                    'name': 'OL/0001',
                    'product_id': self.product1.id,
                    'price_unit': 100.00,
                    'discount': 10,
                    'qty': 1,
                    'tax_ids': False,
                    'price_subtotal': 90.00,
                    'price_subtotal_incl': 90.00,
                }),
                (0, 0, {
                    'name': 'OL/0002',
                    'product_id': self.product2.id,
                    'price_unit': 100.00,
                    'discount': 30,
                    'qty': 1,
                    'tax_ids': False,
                    'price_subtotal': 70.00,
                    'price_subtotal_incl': 70.00,
                })
            ],
            'pricelist_id': self.config.pricelist_id.id,
            'amount_paid': 160.00,
            'amount_total': 160.00,
            'amount_tax': 0.0,
            'amount_return': 0.0,
            'to_invoice': False,
            'date_order': '2026-07-17 18:00:00'  # 14:00 en Caracas -> dentro de 14-16
        })
        #   línea 1 -> discount == 20 y price_subtotal == 80
        self.assertEqual(
            order.lines.filtered(lambda l: l.name == 'OL/0001').discount, 
            20
        )
        self.assertEqual(
            order.lines.filtered(lambda l: l.name == 'OL/0001').price_subtotal, 
            80
        )
        #   línea 2 -> discount == 30 y price_subtotal == 70
        self.assertEqual(
            order.lines.filtered(lambda l: l.name == 'OL/0002').discount, 
            30
        )
        self.assertEqual(
            order.lines.filtered(lambda l: l.name == 'OL/0002').price_subtotal, 
            70
        )
        
        # En este assert comprobamos la limitación:
        #  A pesar de que las lineas sumen 150 luego de aplicar las reglas 
        #  de descuento, la orden queda con el total que 
        #  envió el frontend (160.00).
        #  (!LEER EL README: client-a/pos_schedule_discount_rules/readme.md)
        
        lines_total_sum = sum(line.price_subtotal_incl for line in order.lines)
        self.assertEqual(lines_total_sum, 150.00)
        self.assertEqual(order.amount_total, 160.00)

    def test_order_outside_schedule_no_discount(self):
        """orden fuera del rango -> sin descuento."""
        session_id = self.open_new_session(opening_cash=0)        
        # Las lineas se mantienen igual ya que la orden esta fuera del 
        # rango de horas establecidos (14-16 (UTC -4))
        order = self.PosOrder.create({
            'company_id': self.env.company.id,
            'session_id': session_id.id,
            'partner_id': False,
            'lines': [
                (0, 0, {
                    'name': 'OL/0001',
                    'product_id': self.product1.id,
                    'price_unit': 100.00,
                    'discount': 10,
                    'qty': 1,
                    'tax_ids': False,
                    'price_subtotal': 90.00,
                    'price_subtotal_incl': 90.00,
                }),
                (0, 0, {
                    'name': 'OL/0002',
                    'product_id': self.product2.id,
                    'price_unit': 100.00,
                    'discount': 30,
                    'qty': 1,
                    'tax_ids': False,
                    'price_subtotal': 70.00,
                    'price_subtotal_incl': 70.00,
                })
            ],
            'pricelist_id': self.config.pricelist_id.id,
            'amount_paid': 160.00,
            'amount_total': 160.00,
            'amount_tax': 0.0,
            'amount_return': 0.0,
            'to_invoice': False,
            'date_order': '2026-07-17 21:00:00'  # 17:00 en Caracas -> fuera de rango
        })
        #   línea 1 -> discount == 10 y price_subtotal == 90
        self.assertEqual(
            order.lines.filtered(lambda l: l.name == 'OL/0001').discount, 
            10
        )
        self.assertEqual(
            order.lines.filtered(lambda l: l.name == 'OL/0001').price_subtotal, 
            90
        )
        #   línea 2 -> discount == 30 y price_subtotal == 70
        self.assertEqual(
            order.lines.filtered(lambda l: l.name == 'OL/0002').discount, 
            30
        )
        self.assertEqual(
            order.lines.filtered(lambda l: l.name == 'OL/0002').price_subtotal, 
            70
        )

    def test_overlapping_rules(self):
        with self.assertRaises(ValidationError):
            self.PosDiscountRule.create({
                'name': "Descuento 15-17",
                'hour_from': 15.0,
                'hour_to': 17.0,
                'discount_percentage': 5,
            })
        
        no_overlapping = self.PosDiscountRule.create({
                'name': "Descuento 15-17",
                'hour_from': 16.0,
                'hour_to': 18.0,
                'discount_percentage': 5,
        })

        # El rango de horas de esta regla está en el limite de 
        # la regla 14-16 por lo tanto no se solapan
        # Ver el diagrama en el readme para una 
        # referencia visual de como funciona el 
        # constraint aplicado (client-a/pos_schedule_discount_rules/readme.md)

        self.assertEqual(no_overlapping.name, "Descuento 15-17")
    
    def test_check_hour_from_hour_to(self):
        with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'):
            self.PosDiscountRule.create({
                'name': "Descuento 15-17",
                'hour_from': 20.0,
                'hour_to': 17.0,
                'discount_percentage': 5,
            })

    def test_check_discount_percentage(self):    
        with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'):
            self.PosDiscountRule.create({
                'name': "Descuento 15-17",
                'hour_from': 15.0,
                'hour_to': 17.0,
                'discount_percentage': 200,
            })
        
        with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'):
            self.PosDiscountRule.create({
                'name': "Descuento 15-17",
                'hour_from': 15.0,
                'hour_to': 17.0,
                'discount_percentage': -1,
            })
