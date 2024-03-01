# -*- encoding: utf-8 -*-
{
    "name"      : "Reporte Hoja de Embarque",
    "version"   : "1.0",
    "Summary"   : "Este reporte permite imprimir la Informacion de las entregas.",
    "sequence"  : 50,
    "author"    : "German Ponce Dominguez",
    "category"  : "TMS",
    "description" : """

    """,
    "website" : "http://www.fixdoo.mx",
    "depends" : [
                    "sale",
                    "account",
                    "stock",
                    "sale_stock",
                    "stock_account",
                ],
    "data" : [
                'views/account_move_view.xml',
                'report/account_report_view.xml',
                'report/account_report_labels_view.xml',
            ],
    'installable'   : True,
    'license': 'Other proprietary',

    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: