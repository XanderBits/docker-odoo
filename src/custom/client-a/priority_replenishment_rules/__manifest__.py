{
    'name': 'priority_replenishment_rules',
    'summary': 'Reglas de reabastecimiento por prioridad',
    'description': 'Prioriza productos para reabastecimiento interno según criticidad operativa',
    'license': 'LGPL-3',
    'author': 'Xanderbits - Alexander Amaro',
    'website': 'https://www.binauraldev.com/home',
    'category': 'Inventory/Inventory',
    'version': '0.1',
    'depends': ['stock', 'mail'],
    'data': [
        'data/mail_activity_type.xml',
        'data/ir_cron_data.xml',
        'views/product_template_views.xml',
        'views/menu.xml',
    ]
}
