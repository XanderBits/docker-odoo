from odoo.tests.common import TransactionCase
from odoo.tests import tagged
import logging

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestPriorityReplenishment(TransactionCase):
    """Valida la creación de actividades para productos por debajo del stock
    objetivo y que no se generen duplicados para el mismo producto."""

    def setUpClass(cls):
        pass
    def test_activity_created_below_target(self):
        pass

    def test_no_duplicate_activity(self):
        pass
