{
    'name': 'pos_schedule_discount_rules',
    'summary': 'Reglas de descuento por horario en el punto de venta',
    'description': 'Aplica descuentos automáticos en el punto de venta según '
                    'franjas horarias configurables',
    'license': 'LGPL-3',
    'author': 'Xanderbits - Alexander Amaro',
    'website': 'https://www.binauraldev.com/home',
    'category': 'Sales/Point of Sale',
    'version': '0.1',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/pos_discount_rule_views.xml',
        # 'views/menu.xml',
    ],
    'installable': True,
}
