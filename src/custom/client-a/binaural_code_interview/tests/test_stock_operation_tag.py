from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo import Command 
import logging

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "stock_operation_tag")
class TestStockOperationTag(TransactionCase):
    """Suite de Test relacionados al modelo stock_operation_tag"""

    def setUp(self):
        super(TestStockOperationTag, self).setUp()
        self.StockOperationTag = self.env['stock.operation.tag']
        self.ProductTemplate = self.env['product.template']
    
    def test_create_stock_operation_tag(self):
        _logger.info("*" * 20 + " CREATE_STOCK_OPERATION_TAG " + "*" * 20)
        tag = self.create_tag()
        self.assertEqual(tag.name, "Tag de Prueba")
    
    def test_assign_tag_to_product(self):
        _logger.info("*" * 20 + " TEST_ASSIGN_TAG_TO_PRODUCT " + "*" * 20)
        product = self.create_product()
        tag = self.create_tag()

        product.write({
            'stock_operation_ids': [Command.link(tag.id)]
        })

        self.assertIn(tag, product.stock_operation_ids)
        self.assertIn(product, tag.product_template_ids)

    def create_tag(self):
        tag = self.StockOperationTag.create({
            'name': "Tag de Prueba",
            'description': "Tag de Prueba en suite de test",
            'operation_type': "picking",
        })
        return tag

    def create_product(self):
        product = self.ProductTemplate.create({
            'name': "Producto de prueba"
        })
        return product