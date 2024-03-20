# -*- encoding: utf-8 -*-
###########################################################################
##################### GERMAN PONCE DOMINGUEZ ##############################
###################### german.ponce@outlook.com ###########################
{
    'name': 'Depreciacion Fiscal por medio de INPC',
    'version': '1',
    "author" : "Argil Consulting & German Ponce Dominguez",
    "category" : "Accounting",
    'description': """

    """,
    "website" : "http://poncesoft.blogspot.com",
    "license" : "AGPL-3",
    "depends" : ["account","sale", "account_asset", "report_xlsx"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "account.xml",
                    "assets.xml",
                    "report/report.xml",
                    'security/ir.model.access.csv',
                    ],
    "installable" : True,
    "active" : False,
}
