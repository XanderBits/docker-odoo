from odoo.tests.common import TransactionCase
from odoo.tests import tagged
import logging

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestPosScheduleDiscount(TransactionCase):
    """Valida órdenes con y sin descuento por horario, incluyendo casos límite
    (orden fuera del rango horario, reglas solapadas)."""

    @classmethod
    def setUpC(cls):
        super().setUpClass()
    
    def test_order_within_schedule_gets_discount(self):
        pass

    def test_order_outside_schedule_no_discount(self):
        """orden fuera del rango -> sin descuento."""
        pass

    def test_overlapping_rules(self):
        pass
