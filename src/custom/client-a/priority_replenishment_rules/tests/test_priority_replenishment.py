from odoo.tests.common import TransactionCase
from odoo.tests import tagged
import logging

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestPriorityReplenishment(TransactionCase):
    """Valida la creación de actividades para productos por debajo del stock
    objetivo y que no se generen duplicados para el mismo producto."""

    def setUp(self):
        super(TestPriorityReplenishment, self).setUp()
        self.ProductTemplate = self.env['product.template']
    
    def create_product(self, name='Product01', priority='none', target_stock=1):
        product = self.ProductTemplate.create({
            'name' : name,
            'qty_available': 1,
            'target_stock': target_stock,
            'replenishment_priority' : priority,
        })

        return product

    def _get_activity(self, product):
        res_model_id = self.env.ref('product.model_product_template').id
        activity_type_id = self.env.ref((
                'priority_replenishment_rules'
                '.mail_activity_product_replenishment'
        )).id
        
        activity = self.env['mail.activity'].search([
                ('res_id', '=', product.id),
                ('res_model_id', '=', res_model_id ),
                ('activity_type_id', '=', activity_type_id)
        ])

        return activity

    def test_activity_created_below_target(self):
        product_with_activity = self.create_product(
            name='Producto prioridad Alta para reabastecer',
            target_stock=3, 
            priority='high'
        )
        self.assertEqual(product_with_activity.target_stock, 3)
        self.assertEqual(product_with_activity.qty_available, 1)
        self.assertEqual(product_with_activity.replenishment_priority, 'high')

        self.ProductTemplate._cron_check_target_stock()

        product_replenishment_activity = self._get_activity(product_with_activity)
        self.assertTrue(product_replenishment_activity)
        self.assertEqual(
            product_replenishment_activity.res_id, 
            product_with_activity.id
        )
        self.assertEqual(
            product_replenishment_activity.res_model_id.id, 
            self.env.ref('product.model_product_template').id
        )
        self.assertEqual(
            product_replenishment_activity.activity_type_id.id, 
            self.env.ref((
                'priority_replenishment_rules'
                '.mail_activity_product_replenishment'
            )).id
        )

    def test_activity_not_created(self):
        product_with_no_activity = self.create_product()
        
        self.assertEqual(product_with_no_activity.target_stock, 1)
        self.assertEqual(product_with_no_activity.qty_available, 1)
        self.assertEqual(product_with_no_activity.replenishment_priority, 'none')

        self.ProductTemplate._cron_check_target_stock()

        empty_activity = self._get_activity(product_with_no_activity)
        self.assertFalse(empty_activity)

    def test_no_duplicate_activity(self):
        low_priority_product = self.create_product(
            name='Producto Prioridad Baja',
            target_stock=4, 
            priority='low'
        )
        self.assertEqual(low_priority_product.target_stock, 4)
        self.assertEqual(low_priority_product.qty_available, 1)
        self.assertEqual(low_priority_product.replenishment_priority, 'low')

        self.ProductTemplate._cron_check_target_stock()

        activity_one_ids = self._get_activity(low_priority_product)

        self.assertEqual(len(activity_one_ids), 1)
        self.assertEqual(activity_one_ids[0].res_id, low_priority_product.id)

        low_priority_product.write({'replenishment_priority': 'high'})
        self.ProductTemplate._cron_check_target_stock()
        activity_two_ids = self._get_activity(low_priority_product)

        self.assertEqual(len(activity_two_ids), 1)
        self.assertEqual(activity_two_ids[0].res_id, low_priority_product.id)

