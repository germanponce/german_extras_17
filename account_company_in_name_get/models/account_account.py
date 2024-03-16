# -*- encoding: utf-8 -*-
# Coded by German Ponce Dominguez 
#     ▬▬▬▬▬.◙.▬▬▬▬▬  
#       ▂▄▄▓▄▄▂  
#    ◢◤█▀▀████▄▄▄▄▄▄ ◢◤  
#    █▄ █ █▄ ███▀▀▀▀▀▀▀ ╬  
#    ◥ █████ ◤  
#     ══╩══╩═  
#       ╬═╬  
#       ╬═╬ Dream big and start with something small!!!  
#       ╬═╬  
#       ╬═╬ You can do it!  
#       ╬═╬   Let's go...
#    ☻/ ╬═╬   
#   /▌  ╬═╬   
#   / \
# Cherman Seingalt - german.ponce@outlook.com

import logging
import warnings
import json

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessError, ValidationError
from odoo.osv import expression
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval, time


class AccountAccount(models.Model):
    _inherit ='account.account'

    @api.depends('name', 'code', 'company_id')
    def _compute_display_name(self):
        for account in self:
            company_count = 1
            self.env.cr.execute("select count(*) from res_company;")
            cr_res = self.env.cr.fetchall()
            company_count = cr_res[0][0]
            display_name = ""
            if company_count > 1:
                display_name = account.code + ' ' + account.name + ' [' + account.company_id.name + ']'
            else:
                display_name = account.code + ' ' + account.name

            account.display_name = display_name

class AccountAnalyticAccount(models.Model):
    _inherit ='account.analytic.account'

    @api.depends('name', 'code', 'company_id')
    def _compute_display_name(self):
        for account in self:
            company_count = 1
            self.env.cr.execute("select count(*) from res_company;")
            cr_res = self.env.cr.fetchall()
            company_count = cr_res[0][0]
            display_name = ""
            if company_count > 1:
                if account.code:
                    display_name = account.code + ' ' + account.name + ' [' + account.company_id.name + ']'
                else:
                    display_name = account.name + ' [' + account.company_id.name + ']'
            else:
                if account.code:
                    display_name = account.code + ' ' + account.name
                else:
                    display_name = account.name

            account.display_name = display_name