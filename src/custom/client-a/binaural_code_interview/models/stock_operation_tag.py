from odoo import models, fields
from random import randint


class StockOperationTag(models.Model):
    _name = 'stock.operation.tag'
    _inherit = ['mail.thread']
    _description = 'Etiqueta operativa de inventario'

    def _get_default_color(self):
        return randint(1, 11)
    
    OPERATION_TYPE_SELECTION = [
        ('picking','Picking'),
        ('storage','Almacenamiento'),
        ('dispatch','Despacho'),
    ]

    name = fields.Char(
        string='Nombre', 
        required=True,
        help='Nombre para la etiqueta'
    )
    color = fields.Integer(
        string='Color',
        default=_get_default_color,
        help='Color representativo'
    )
    description = fields.Text(
        string='Descripción', 
        help='Descripción de la etiqueta'
    )
    operation_type = fields.Selection(
        OPERATION_TYPE_SELECTION,
        required=True,
        string='Tipo de operación',
        help='Tipo de operación correspondiente a esta etiqueta'
    )

    product_template_ids = fields.Many2many(
        string="Productos Relacionados",
        comodel_name='product.template',
        relation='product_template_stock_operation_tag_rel',
    )
