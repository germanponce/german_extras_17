# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2021 German Ponce Dominguez
#
##############################################################################

{
    'name' : 'Bloqueo de Precio Unitario',
    'category': 'Sales',
    'version': '1.0',
    'author': 'Fixdoo, German Ponce Dominguez',
    'website': 'https://fixdoo.mx',
    'description': """
        Tarifas Avanzadas
    """,
    'summary': 'Este modulo permite bloquear el cambio de precio.',
    'depends' : [
                    'base', 
                    'product', 
                    'sale'
                ],
    'price': 1000,
    'currency': 'USD',
    'license': 'OPL-1',
    'data': [
        'views/sale_view.xml',
        "security/groups_access.xml",
        "security/ir.model.access.csv",
    ],
    'demo': [],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: