from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_operation_ids = fields.Many2many(
        comodel_name='stock.operation.tag', 
        string='Etiquetas Operativas',
        relation='product_template_stock_operation_tag_rel'
    )