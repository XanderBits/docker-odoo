from odoo import _
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tests import tagged
import logging

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "testing_binaural_interview")
class TestBinauralInterview(TransactionCase):
    """Scaffold inicial, esto luego posiblemente le cambie el nombre o lo sustituya."""

    def setUp(self):
        super(TestBinauralInterview, self).setUp()
        self.test = "Probando test"

    
    def test_binaural_interview(self):
        _logger.info("*" * 50 + " Iniciando test " + "*" * 50)
        self.assertEqual(self.test, "Probando testttttts")
        _logger.info("*" * 50 + " FIN " + "*" * 50)