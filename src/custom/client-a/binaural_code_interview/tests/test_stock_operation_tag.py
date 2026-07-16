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
    
    def create_tag(self, operation_type='picking', name='Tag de Prueba', 
                description=''):
        tag = self.StockOperationTag.create({
            'name': name,
            'description': description,
            'operation_type': operation_type,
        })
        return tag

    def create_product(self, name="Producto de prueba", stock_operation_ids=False):
        product = self.ProductTemplate.create({
            'name': name,
            'stock_operation_ids': stock_operation_ids
        })
        return product

    def create_tag_ids(self):
        tag_ids = {
            'picking': self.create_tag(
                        name='Tag Prueba 01', 
                        description='Tag de picking'
            ),
            'storage': self.create_tag(
                        operation_type='storage',
                        name='Tag Prueba 02', 
                        description='Tag de storage'
            ),
            'dispatch': self.create_tag(
                        operation_type='dispatch',
                        name='Tag Prueba 03', 
                        description='Tag de dispatch'
            ),
        }
        return tag_ids

    def test_create_stock_operation_tag(self):
        _logger.info("*" * 20 + " CREATE_STOCK_OPERATION_TAG " + "*" * 20)
        tag = self.create_tag()
        self.assertEqual(tag.name, "Tag de Prueba")
    
    def test_assign_tag_to_product(self):
        _logger.info("*" * 20 + " TEST_ASSIGN_TAG_TO_PRODUCT " + "*" * 10)
        product = self.create_product()
        tag = self.create_tag()

        product.write({
            'stock_operation_ids': [Command.link(tag.id)]
        })

        self.assertIn(tag, product.stock_operation_ids)
        self.assertIn(product, tag.product_template_ids)

    def test_verify_group_by_kanban(self):
        _logger.info("*" * 20 + " VERIFICANDO AGRUPACIÓN EN EL KANBAN " + "*" * 20)
        tag_ids = self.create_tag_ids()

        self.create_product(
            name="Producto Prueba 01", 
            stock_operation_ids=[
                Command.set(
                    [tag_ids['dispatch'].id]
                )
            ]
        )
        self.create_product(
            name="Producto Prueba 02",
            stock_operation_ids=[
                Command.set(
                    [tag_ids['picking'].id, tag_ids['storage'].id]
                )
            ]
        )
        self.create_product(
            name="Producto Prueba 03",
            stock_operation_ids=[
                Command.set(
                    [tag_ids['storage'].id]
                )
            ]
        )

        product_qty = self.ProductTemplate._read_group(
            [('stock_operation_ids', '!=', False)],
            ['stock_operation_ids'],
            ['id:count']
        )

        counts = {tag: count for tag, count in product_qty}
        _logger.info((
            f"CANTIDAD DE PRODUCTOS: {sum(counts.values())}"
        ))
        _logger.info((
            f"EL TIPO DE OPERACIÓN STORAGE TIENE "
            f"{counts[tag_ids['storage']]} PRODUCTOS"
        ))
        self.assertIn(tag_ids['storage'], counts)
        self.assertEqual(counts[tag_ids['storage']], 2)
        self.assertEqual(sum(counts.values()), 4)