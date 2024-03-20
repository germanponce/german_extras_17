# -*- encoding: utf-8 -*-
###########################################################################
##################### GERMAN PONCE DOMINGUEZ ##############################
###################### german.ponce@outlook.com ###########################

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import datetime

import logging
_logger = logging.getLogger(__name__)

from datetime import datetime, date

import csv
import requests


class AccountAssetAsset(models.Model):
    _name = 'account.asset.asset'
    _inherit ='account.asset.asset'

    inpc_mitad = fields.Float('INPC Mitad del periodo', digits=(14,4))

    inpc_adquisicion = fields.Float('INPC Fecha de Adquisicion', digits=(14,4))

    inpc_factor = fields.Float('Factor', digits=(14,4))

    inpc_depresiacion = fields.Monetary('Depreciacion del Ejercicio actualizada')

    last_asset_control_id = fields.Many2one('banxico.inpc.data.assets.control', 'Ultima Depreciacion')

    inpc_adquisicion_first_period_id = fields.Many2one('account.period', 'Primer Mitad del Periodo - Compra')

    def self_asset_refresh_inpc_data(self,):
        _logger.info("\n::::::::::: assets_refresh_inpc_data >>>>>>>> ")
        account_period = self.env['account.period']
        fiscal_year = self.env['account.fiscalyear']
        banxico_data = self.env['banxico.inpc.data']
        banxico_asset_control_obj = self.env['banxico.inpc.data.assets.control']
        #### SE VA USAR EL PERIODO INICIAL CUANDO NO EXISTA UN PERIDO EN PROCESO #####
        banxico_data_open_ids = banxico_data.search([('state','=','process')])
        _logger.info("\n:::::::::::: banxico_data_open_ids: %s >>>>>>>  " % banxico_data_open_ids)
        if banxico_data_open_ids:
            for rec in self:
                for inpc_data in banxico_data_open_ids:
                    banxico_asset_contro_rel = banxico_asset_control_obj.search([('data_id','=',inpc_data.id),
                                                                         ('asset_id','=', rec.id)])
                    if banxico_asset_contro_rel:
                        banxico_asset_contro_rel.compute_inpc_control()
                    else:
                        raise UserError("El activo no se encuentra relacionado con el INPC %s" % inpc_data.year_id.name)
            
    #### Actualizacion informacion de Activos
    @api.model
    def update_inpc_assets(self):
        _logger.info("\n:::::::::::: Actualizando la informacion de Activos (INPC). Fecha: %s >>>>>>>  " % fields.Date.context_today(self))
        _logger.info("\n::::::::::: update_inpc_assets >>>>>>>> ")
        account_period = self.env['account.period']
        fiscal_year = self.env['account.fiscalyear']
        banxico_data = self.env['banxico.inpc.data']
        #### SE VA USAR EL PERIODO INICIAL CUANDO NO EXISTA UN PERIDO EN PROCESO #####
        banxico_data_open_ids = banxico_data.search([('state','=','process')])
        _logger.info("\n:::::::::::: banxico_data_open_ids: %s >>>>>>>  " % banxico_data_open_ids)
        if banxico_data_open_ids:
            for inpc_data in banxico_data_open_ids:
                inpc_data.compute_inpc_assets()
    