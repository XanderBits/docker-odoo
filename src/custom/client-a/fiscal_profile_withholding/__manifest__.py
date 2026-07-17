{
    'name': 'fiscal_profile_withholding',
    'summary': 'Retenciones automáticas por perfil fiscal',
    'description': 'Aplica retenciones automáticas en facturas según el perfil fiscal '
                    'del cliente/proveedor, mediante una tabla de reglas configurable.',
    'license': 'LGPL-3',
    'author': 'Xanderbits - Alexander Amaro',
    'website': 'https://www.binauraldev.com/home',
    'category': 'Accounting/Accounting',
    'version': '0.1',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/withholding_rule_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
