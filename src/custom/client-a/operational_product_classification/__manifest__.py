{
    'name': 'operational_product_classification',
    'summary': 'Modulo para prueba tecnica Binaural Julio 2026',
    'description': 'Permitir clasificar productos con etiquetas operativas para optimizar las operaciones de inventario',
    'license': 'LGPL-3',
    'author': 'Xanderbits - Alexander Amaro',
    'website': 'https://www.binauraldev.com/home',
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'stock', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/stock_operation_tag_views.xml',
        'views/menu.xml'
    ]
}

