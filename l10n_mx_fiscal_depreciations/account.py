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



class BanxicoInpcDataAssetsWizard(models.TransientModel):
    _name = 'banxico.inpc.data.assets.wizard'
    _description = 'Asistente Insertar Activos'

    asset_ids = fields.Many2many('account.asset.asset', 'inpc_wizard_asset_rel', 'wizard_id', 'asset_id', 'Activos')


    def action_insert(self):
        active_ids = self._context['active_ids']
        for active_id in active_ids:
            control_obj = self.env['banxico.inpc.data.assets.control']
            for asset in self.asset_ids:
                exist_data = control_obj.search([('asset_id','=',asset.id),('data_id','=',active_id)])
                if not exist_data:
                    vals = {
                        'asset_id': asset.id,
                        'data_id': active_id,
                    }
                    control_id = control_obj.create(vals)
        return True
   

class BanxicoInpcData(models.Model):
    _name = 'banxico.inpc.data'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Lista de Precios al Consumidor'
    _rec_name = "year_id"
    _order = 'year_id' 

    @api.depends('inpc_period_lines')
    def _get_last_period(self):
        for rec in self:
            if rec.inpc_period_lines:
                rec.current_period = rec.inpc_period_lines[-1].period_id.id

    @api.depends('inpc_period_lines')
    def _get_last_inpc(self):
        for rec in self:
            if rec.inpc_period_lines:
                rec.inpc_current = rec.inpc_period_lines[-1].inpc

    year_id = fields.Many2one('account.fiscalyear', 'Año')

    current_period = fields.Many2one('account.period', 'Periodo Actual', compute="_get_last_period", store=True)

    inpc_current = fields.Float('INPC Actual', digits=(14,4), compute="_get_last_inpc", store=True)

    inpc_period_lines = fields.One2many('banxico.inpc.data.period', 'data_id', 'Periodos INPC')

    inpc_assets_lines = fields.One2many('banxico.inpc.data.assets.control', 'data_id', 'Activos')

    state = fields.Selection([('draft','Borrador'),('process','En proceso'),('done','Hecho')], string="Estado", default='draft')


    @api.constrains('state')
    def _constraint_state(self):
        for rec in self:
            if rec.state == 'process':
                other_inpc_records = self.search([('state','=','process'),('id','!=',rec.id)])
                if other_inpc_records:
                    raise ValidationError("Solo se puede tener un registro de calculo INPC en proceso.")
        return True
    

    def action_draft(self):
        for rec in self:
            rec.state='draft'
        return True

    def action_process(self):
        for rec in self:
            rec.state='process'
        return True

    def action_done(self):
        for rec in self:
            rec.state='done'
        return True

    def compute_inpc_assets(self):
        for rec in self:
            if rec.inpc_assets_lines:
                for line_asset in rec.inpc_assets_lines:
                    line_asset.compute_inpc_control()
        return True
    
class BanxicoInpcDataPeriod(models.Model):
    _name = 'banxico.inpc.data.period'
    _description = 'Lista de Precios al Consumidor Periodos'
    _rec_name = "period_id"
    _order = 'period_id' 

    @api.depends('period_id')
    def _get_period_name(self):
        name_months = {
            1: 'Enero',
            2: 'Febrero',
            3: 'Marzo',
            4: 'Abril',
            5: 'Mayo',
            6: 'Junio',
            7: 'Julio',
            8: 'Agosto',
            9: 'Septiembre',
            10: 'Octubre',
            11: 'Noviembre',
            12: 'Diciembre',
        }
        for rec in self:
            if rec.period_id:
                name_compute = ""
                period_split = rec.period_id.name.split('/')
                period_number = int(period_split[0])
                period_name = name_months[period_number]
                year_name = period_split[1]
                name_compute = period_name[0:3]+' '+year_name
                rec.period_name = name_compute


    data_id = fields.Many2one('banxico.inpc.data', 'ID Ref')

    period_id = fields.Many2one('account.period', 'Periodo')

    period_name = fields.Char('Descripción', compute="_get_period_name")

    inpc = fields.Float('INPC', digits=(14,4))


class BanxicoInpcDataAssetsControl(models.Model):
    _name = 'banxico.inpc.data.assets.control'
    _description = 'Control de los Activos y el Año para su depreciacion INPC' 
    _rec_name = 'asset_id' 

    def _get_currency_company(self):
        current_company = self.env.user.company_id
        currency_id = current_company.currency_id.id
        for rec in self:
            rec.currency_id = currency_id

    data_id = fields.Many2one('banxico.inpc.data', 'Año Lista INPC')

    asset_id = fields.Many2one('account.asset.asset', 'Activo')

    value = fields.Float('Valor Bruto', related="asset_id.value")

    inpc_mitad = fields.Float('INPC Mitad del periodo', digits=(14,4))

    inp_mitad_period_id = fields.Many2one('banxico.inpc.data.period', 'Periodo')

    inpc_adquisicion = fields.Float('INPC Fecha de Adquisicion', digits=(14,4))

    inpc_adquisicion_period_id = fields.Many2one('banxico.inpc.data.period', 'Periodo')

    inpc_factor = fields.Float('Factor', digits=(14,4))

    inpc_depresiacion = fields.Float('Depreciacion del Ejercicio actualizada')

    compute_done = fields.Boolean('INPC Calculado')

    currency_id = fields.Many2one('res.currency', compute="_get_currency_company")

    # @api.constrains('asset_id')
    # def _constraint_asset_id(self):
    #     for rec in self:
    #         exist_data = self.search([('asset_id','=',rec.asset_id.id),('data_id','=',rec.data_id.id)])
    #         print ("### exist_data >>>>>>>>>> ",exist_data)
    #         if exist_data:
    #             raise UserError("El activo ya se encuentra dentro del Ejercicio.") 
    #     return True


    @api.onchange('inpc_mitad','inpc_adquisicion')
    def onchange_compute_factor(self):
        if self.inpc_mitad and self.inpc_adquisicion:
            inpc_factor = 0.0
            try:
                inpc_factor = self.inpc_mitad / self.inpc_adquisicion
            except:
                inpc_factor = 0.0
            ######### Modificaciones Julio 2021 ########
            if inpc_factor > 0.0 and inpc_factor < 1.0:
                inpc_factor = 1.0
            ############################################
            self.inpc_factor =  inpc_factor
            if self.asset_id:
                try:
                    value = self.asset_id.value - self.asset_id.value_residual
                except:
                    value = self.asset_id.value_residual
                self.inpc_depresiacion = inpc_factor * value


    @api.model
    def create(self, vals):
        asset_id = vals.get('asset_id', False)
        data_id = vals.get('data_id', False)
        if asset_id and data_id:
            exist_data = self.search([('asset_id','=',asset_id),('data_id','=',data_id)])
            if exist_data:
                raise UserError("El activo ya se encuentra dentro del Ejercicio.") 
        res = super(BanxicoInpcDataAssetsControl, self).create(vals)
        return res

    def validation_manual_data(self):
        ### Al final escribimos el resultado en el Activo ###
        inpc_mitad = self.inpc_mitad
        inpc_adquisicion = self.inpc_adquisicion
        inpc_factor = self.inpc_factor
        inpc_depresiacion = self.inpc_depresiacion
        if inpc_mitad and inpc_adquisicion and inpc_factor and inpc_depresiacion:
            if self.asset_id:
                self.asset_id.inpc_mitad = self.inpc_mitad
                self.asset_id.inpc_adquisicion = self.inpc_adquisicion
                self.asset_id.inpc_factor = self.inpc_factor
                self.asset_id.inpc_depresiacion = self.inpc_depresiacion
                self.asset_id.last_asset_control_id = self.id
            if self.inpc_depresiacion:
                self.compute_done = True
            return True
        else:
            return False

    def reset_contro_and_asset_null(self, control_br, asset_br):
        if control_br.asset_id:
            dict_vals = {
                'inpc_mitad': 0.0,
                'inpc_factor': 0.0,
                'inpc_depresiacion': 0.0,
                'last_asset_control_id': control_br.id,
            }
            self.update_vals_query_asset_id(dict_vals, asset_br.id)
        if control_br.inpc_depresiacion:
            control_br.compute_done = False
        ### Limpiamos los Calculos - Registro de Control ###
        control_br.inpc_mitad = 0.0
        control_br.inp_mitad_period_id = False
        control_br.inpc_factor = 0.0
        control_br.inpc_depresiacion = 0.0 
        
        return True
    
    def update_vals_query_asset_id(self, dict_vals, asset_id):
        cr = self.env.cr
        for val in dict_vals.keys():
            field_nm = val
            val_data = dict_vals[val]
            if type(val_data) == str:
                cr.execute("""
                    update account_asset_asset set %s='%s' where id=%s;
                    """ % (field_nm, val_data, asset_id))
            elif type(val_data) == int:
                cr.execute("""
                    update account_asset_asset set %s=%s where id=%s;
                    """ % (field_nm, val_data, asset_id))
            elif type(val_data) == float:
                cr.execute("""
                    update account_asset_asset set %s=%s where id=%s;
                    """ % (field_nm, val_data, asset_id))
            else:
                cr.execute("""
                    update account_asset_asset set %s=%s where id=%s;
                    """ % (field_nm, val_data, asset_id))
    @api.multi
    def compute_inpc_control(self):
        account_period = self.env['account.period']
        fiscal_year = self.env['account.fiscalyear']
        banxico_data = self.env['banxico.inpc.data']
        banxico_data_period = self.env['banxico.inpc.data.period']
        for rec in self:
            if rec.data_id.state != 'process':
                raise ValidationError("No se puede calcular la información en periodos Cerrados o Borrador.")
            # exist_data = rec.validation_manual_data()
            # if exist_data:
            #     return True
            fiscal_year_id = rec.data_id.year_id
            asset_br = rec.asset_id
            if not fiscal_year_id:
                continue
            ####### Fechas y Periodos del Año a Calcular ########
            #### Fecha, Periodo y Año - Ejercicio Fiscal #####
            fiscal_year_date_start = fiscal_year_id.date_start
            fiscal_year_year = fiscal_year_date_start.year
            fiscal_year_month = fiscal_year_date_start.month

            #### Fecha, Periodo y Año de la Fecha en Curso #####
            #### Borrar --> Solo temporal para Pruebas ###
            # date_time_str = '2021-02-01'
            # current_date = datetime.strptime(date_time_str, '%Y-%m-%d')
            #### Descomentar 
            current_date = date.today()
            current_year = current_date.year
            current_month = current_date.month

            #### Fecha, Periodo y Año de Compra del Activo  #####
            date_acquirer = asset_br.date
            acquirer_year = date_acquirer.year
            acquirer_month = date_acquirer.month

            if acquirer_year < fiscal_year_year:
                _logger.info("\n########## Activo de años pasados - Se calcula mensualmente el INPC >>>>>> ")
                if current_month == 1:
                    _logger.info("\n### Enero borra el INPC aun no se puede calcular iniciamos en 0.0 >>>>>>>> ")
                    ### Limpiamos los Calculos - Activo ###
                    self.reset_contro_and_asset_null(rec, rec.asset_id)

                else:
                    if current_month in (3,5,7,9,11):
                        _logger.info("\n### Los meses impares 3,5,7,9,11 no modifican o afectan el INPC >>>>>>>> ")
                        _logger.info("\n### Recalculamos los INPC de los meses pares >>>>>>>> ")
                        middle_month = current_month / 2
                        middle_month = int(middle_month)
                        _logger.info("\n##################### middle_month_final >>>>>>>>>>>>>>>>> %s " % middle_month)
                        middle_month_str = str(middle_month)
                        if middle_month < 10:
                            middle_month_str = '0%s' % str(int(middle_month))
                        period_middle_compute = account_period.search([('name','=','%s/%s' % (middle_month_str, fiscal_year_year))])
                        if period_middle_compute:
                            banxico_data_period_id = banxico_data_period.search([('period_id','=',period_middle_compute.id)], limit=1)
                            if banxico_data_period_id:
                                rec.inpc_mitad = banxico_data_period_id.inpc
                                rec.inp_mitad_period_id = banxico_data_period_id.id
                            else:
                                ### Limpiamos los Calculos ###
                                self.reset_contro_and_asset_null(rec, rec.asset_id)
                                _logger.info("\n########## Aun no existe el periodo '%s/%s' dentro del Catalogo INPC actual - No se ingresara la informacion >>>>>> " % (fiscal_year_year, middle_month_str) )
                        else:
                            ### Limpiamos los Calculos ###
                            self.reset_contro_and_asset_null(rec, rec.asset_id)
                            _logger.info("\n########## Aun no existe el periodo '%s/%s' - No se ingresara la informacion >>>>>> " % (fiscal_year_year, middle_month_str) )
                        # return True
                    else:
                        _logger.info("\n### Recalculamos los INPC de los meses pares >>>>>>>> ")
                        middle_month = current_month / 2
                        _logger.info("\n##################### middle_month_final >>>>>>>>>>>>>>>>> %s " % middle_month)
                        middle_month_str = str(middle_month)
                        if middle_month < 10:
                            middle_month_str = '0%s' % str(int(middle_month))
                        period_middle_compute = account_period.search([('name','=','%s/%s' % (middle_month_str, fiscal_year_year))])
                        if period_middle_compute:
                            banxico_data_period_id = banxico_data_period.search([('period_id','=',period_middle_compute.id)], limit=1)
                            if banxico_data_period_id:
                                rec.inpc_mitad = banxico_data_period_id.inpc
                                rec.inp_mitad_period_id = banxico_data_period_id.id
                            else:
                                ### Limpiamos los Calculos ###
                                self.reset_contro_and_asset_null(rec, rec.asset_id)
                                _logger.info("\n########## Aun no existe el periodo '%s/%s' dentro del Catalogo INPC actual - No se ingresara la informacion >>>>>> " % (fiscal_year_year, middle_month_str) )
                        else:
                            ### Limpiamos los Calculos ###
                            self.reset_contro_and_asset_null(rec, rec.asset_id)
                            _logger.info("\n########## Aun no existe el periodo '%s/%s' - No se ingresara la informacion >>>>>> " % (fiscal_year_year, middle_month_str) )

            else:
                _logger.info("\n########## Activo se compro en el mismo año - Se calculara su primer mitad de Periodo >>>>>> ")
                compute_fist_period_middle = True # Variable para determinar si recalculamos su primer INPC Mitad de Periodo
                if acquirer_month == 11:
                    compute_fist_period_middle = False
                    _logger.info("\n########## En el Periodo '%s/%s' de compra el INPC primer mitad del Periodo se queda igual >>>>>> " % (fiscal_year_year, '11') )

                    middle_month_str = '11'
                    period_middle_compute = account_period.search([('name','=','%s/%s' % (middle_month_str, fiscal_year_year))])
                    if period_middle_compute:
                        banxico_data_period_id = banxico_data_period.search([('period_id','=',period_middle_compute.id)], limit=1)
                        if rec.asset_id:
                            #rec.asset_id.inpc_adquisicion_first_period_id = period_middle_compute.id
                            dict_vals = {
                                    'inpc_adquisicion_first_period_id': period_middle_compute.id,
                                }
                            self.update_vals_query_asset_id(dict_vals, rec.asset_id.id)

                        if banxico_data_period_id:
                            rec.inpc_mitad = banxico_data_period_id.inpc
                            rec.inp_mitad_period_id = banxico_data_period_id.id
                        else:
                            ### Limpiamos los Calculos ###
                            self.reset_contro_and_asset_null(rec, rec.asset_id)
                            _logger.info("\n########## Aun no existe el periodo '%s/%s' dentro del Catalogo INPC actual - No se ingresara la informacion >>>>>> " % (fiscal_year_year, '11') )
                    else:
                        ### Limpiamos los Calculos ###
                        self.reset_contro_and_asset_null(rec, rec.asset_id)
                        _logger.info("\n########## Aun no existe el periodo '%s/%s' - No se ingresara la informacion >>>>>> " % (fiscal_year_year, '11') )

                if acquirer_month == 12:
                    compute_fist_period_middle = False
                    self.reset_contro_and_asset_null(rec, rec.asset_id)
                    _logger.info("\n########## En el Periodo '%s/%s' de compra no se puede recalcular el primer INPC mitad del Periodo >>>>>> " % (fiscal_year_year, '12') )
                    self.env.cr.execute("""
                                update account_asset_asset set inpc_adquisicion_first_period_id = null where id=%s;
                                """ % (rec.asset_id.id, ))

                if compute_fist_period_middle:
                    _logger.info("\n### EL AÑO ES EL MISMO QUE ESTAMOS CALCULANDO >>>>>>>> ")
                    middle_month = (12 - acquirer_month)
                    _logger.info("\n##################### middle_month >>>>>>>>>>>>>>>>>>> %s " % middle_month)
                    months_aditional = float(middle_month)/2
                    _logger.info("\n##################### months_aditional >>>>>>>>>>>>>>>>> %s " % months_aditional)
                    middle_month_final = int(acquirer_month+months_aditional)
                    _logger.info("\n##################### middle_month_final >>>>>>>>>>>>>>>>> %s " % middle_month_final)
                    middle_month_str = str(middle_month_final)
                    if middle_month_final < 10:
                        middle_month_str = '0%s' % str(int(middle_month_final))
                    _logger.info("\n##################### primer INPC mitad del periodo >>>>>>>>>>>>>>>>> %s " % middle_month_final)
                    
                    period_middle_compute = account_period.search([('name','=','%s/%s' % (middle_month_str, fiscal_year_year))])
                    if period_middle_compute:
                        banxico_data_period_id = banxico_data_period.search([('period_id','=',period_middle_compute.id)], limit=1)
                        if rec.asset_id:
                            #rec.asset_id.inpc_adquisicion_first_period_id = period_middle_compute.id
                            dict_vals = {
                                    'inpc_adquisicion_first_period_id': period_middle_compute.id,
                            }
                            self.update_vals_query_asset_id(dict_vals, rec.asset_id.id)
                        if banxico_data_period_id and banxico_data_period_id.inpc > 0.0:
                            rec.inpc_mitad = banxico_data_period_id.inpc
                            rec.inp_mitad_period_id = banxico_data_period_id.id
                        else:
                            self.reset_contro_and_asset_null(rec, rec.asset_id)
                            _logger.info("\n########## Aun no existe el periodo '%s/%s' - No se ingresara la informacion >>>>>> " % (fiscal_year_year, middle_month_str) )

                #### Cuando calculemos su primer Mitad del periodo de Compra por el año actual ####
                #### Guardamos el Periodo en el campos -> inpc_adquisicion_first_period_id

                ##### Verificamos si no tiene su primer INPC Mitad del Periodo ######
                #::: Si tiene:
                ##### Verificamos si el Periodo actual ya es el mismo de su primer INPC Mitad del Periodo ######
                #::: Si ya es el mismo periodo:
                #::: Insertamos los datos de inpc_mitad - inpc_factor - inpc_depresiacion
                #::: Si no es el mismo periodo:
                ##### Continuamos esperando
                    
                ##### Si ya tiene un INPC Mitad del Periodo #######
                #::: Si el periodo actual es mayor a su primer INPC Mitad del Periodo:
                ##### Calculamos normal meses transcurridos - # periodo actual / 2

            acquirer_month_str = str(acquirer_month)
            if acquirer_month < 10:
                acquirer_month_str = '0%s' % str(int(acquirer_month))
            period_acquirer = account_period.search([('name','=','%s/%s' % (acquirer_month_str, acquirer_year))])  
            _logger.info("\n##################### period_acquirer >>>>>>>>>>>>>>>>> %s " % period_acquirer)
            _logger.info("\n##################### acquirer_month_str >>>>>>>>>>>>>>>>> %s " % acquirer_month_str)

            #### Buscamos e insertamos el INPC para la Fecha de Adquisicion ####
            if period_acquirer:
                banxico_data_period_acquirer_id = banxico_data_period.search([('period_id','=',period_acquirer.id)], limit=1)
                _logger.info("\n##################### banxico_data_period_acquirer_id >>>>>>>>>>>>>>>>> %s " % banxico_data_period_acquirer_id)
                if banxico_data_period_acquirer_id:
                    rec.inpc_adquisicion = banxico_data_period_acquirer_id.inpc
                    rec.inpc_adquisicion_period_id = banxico_data_period_acquirer_id.id
                else:
                    _logger.info("\n########## Aun no existe el periodo de Acquisicion - No se ingresara la informacion >>>>>> ")
                    self.reset_contro_and_asset_null(rec, rec.asset_id)
            
            # raise UserError("Calculando el INPC para el activo")
            
            if rec.inpc_mitad and rec.inpc_adquisicion:
                inpc_factor = 0.0
                try:
                    inpc_factor = rec.inpc_mitad / rec.inpc_adquisicion
                except:
                    inpc_factor = 0.0
                ######### Modificaciones Julio 2021 ########
                if inpc_factor > 0.0 and inpc_factor < 1.0:
                    inpc_factor = 1.0
                ############################################
                rec.inpc_factor =  inpc_factor
                if rec.asset_id:
                    # value = rec.asset_id.value_residual
                    try:
                        value = rec.asset_id.value - rec.asset_id.value_residual
                    except:
                        value = rec.asset_id.value_residual
                    rec.inpc_depresiacion = inpc_factor * value
            # Al final escribimos el resultado en el Activo ###
            if rec.asset_id:
                # rec.asset_id.inpc_mitad = rec.inpc_mitad
                # rec.asset_id.inpc_adquisicion = rec.inpc_adquisicion
                # rec.asset_id.inpc_factor = rec.inpc_factor
                # rec.asset_id.inpc_depresiacion = rec.inpc_depresiacion
                # rec.asset_id.last_asset_control_id = rec.id
                dict_vals = {
                        'inpc_mitad': rec.inpc_mitad,
                        'inpc_factor': rec.inpc_factor,
                        'inpc_adquisicion': rec.inpc_adquisicion,
                        'inpc_depresiacion': rec.inpc_depresiacion, 
                        'last_asset_control_id': rec.id,
                }
                self.update_vals_query_asset_id(dict_vals, rec.asset_id.id)

            if rec.inpc_depresiacion:
                rec.compute_done = True
        ### BORRAR ###
        return True
        #raise UserError("Calculando el INPC para el activo")


    @api.multi
    def compute_inpc_control_backup(self):
        account_period = self.env['account.period']
        fiscal_year = self.env['account.fiscalyear']
        banxico_data = self.env['banxico.inpc.data']
        banxico_data_period = self.env['banxico.inpc.data.period']
        for rec in self:
            if rec.data_id.state != 'process':
                raise ValidationError("No se puede calcular la información en periodos Cerrados o Borrador.")
            exist_data = rec.validation_manual_data()
            if exist_data:
                return True
            fiscal_year_id = rec.data_id.year_id
            asset_br = rec.asset_id
            if not fiscal_year_id:
                continue
            ####### Fechas y Periodos del Año a Calcular ########
            current_depreciation_date_start = fiscal_year_id.date_start
            # current_year = date.today().year
            current_year = current_depreciation_date_start.year
            current_month = current_depreciation_date_start.month
            current_month_str = str(current_month)
            if current_month < 10:
                current_month_str = '0%s' % str(int(current_month))
            asset_date = asset_br.date
            asset_year = asset_date.year
            period_06 = account_period.search([('name','=','06/%s' % current_year)])
            ####### Periodo de Adquisicion  ###########
            date_acquirer = asset_br.date
            acquirer_year = date_acquirer.year
            acquirer_month = date_acquirer.month
            acquirer_month_str = str(acquirer_month)
            if acquirer_month < 10:
                acquirer_month_str = '0%s' % str(int(acquirer_month))
            period_acquirer = account_period.search([('name','=','%s/%s' % (acquirer_month_str, acquirer_year))])
            if asset_year < current_year:
                _logger.info("\n########## Activo de años pasados - Se tomara el INPC de Junio >>>>>> ")
                banxico_data_period_id = banxico_data_period.search([('period_id','=',period_06.id)], limit=1)
                if banxico_data_period_id:
                    rec.inpc_mitad = banxico_data_period_id.inpc
                    rec.inp_mitad_period_id = banxico_data_period_id.id
                else:
                    _logger.info("\n########## Aun no existe Junio - No se ingresara la informacion >>>>>> ")

            else:
                _logger.info("\n### EL AÑO ES EL MISMO QUE ESTAMOS CALCULANDO >>>>>>>> ")
                middle_month = (12 - acquirer_month)
                _logger.info("\n##################### middle_month >>>>>>>>>>>>>>>>>>> %s " % middle_month)
                months_aditional = float(middle_month)/2
                _logger.info("\n##################### months_aditional >>>>>>>>>>>>>>>>> %s " % months_aditional)
                middle_month_final = int(acquirer_month+months_aditional)
                _logger.info("\n##################### middle_month_final >>>>>>>>>>>>>>>>> %s " % middle_month_final)
                middle_month_str = str(middle_month_final)
                if middle_month_final < 10:
                    middle_month_str = '0%s' % str(int(middle_month_final))
                period_middle_compute = account_period.search([('name','=','%s/%s' % (middle_month_str, acquirer_year))])
                if period_middle_compute:
                    banxico_data_period_id = banxico_data_period.search([('period_id','=',period_middle_compute.id)], limit=1)
                    if banxico_data_period_id:
                        rec.inpc_mitad = banxico_data_period_id.inpc
                        rec.inp_mitad_period_id = banxico_data_period_id.id
                    else:
                        _logger.info("\n########## Aun no existe el periodo '%s/%s' dentro del Catalogo INPC actual - No se ingresara la informacion >>>>>> " % (acquirer_year, middle_month_str) )
                else:
                    _logger.info("\n########## Aun no existe el periodo '%s/%s' - No se ingresara la informacion >>>>>> " % (acquirer_year, middle_month_str) )

            #### Buscamos e insertamos el INPC para la Fecha de Adquisicion ####
            if period_acquirer:
                banxico_data_period_acquirer_id = banxico_data_period.search([('period_id','=',period_acquirer.id)], limit=1)
                if banxico_data_period_acquirer_id:
                    rec.inpc_adquisicion = banxico_data_period_acquirer_id.inpc
                    rec.inpc_adquisicion_period_id = banxico_data_period_acquirer_id.id
                else:
                    _logger.info("\n########## Aun no existe el periodo de Acquisicion - No se ingresara la informacion >>>>>> ")

            if rec.inpc_mitad and rec.inpc_adquisicion:
                inpc_factor = 0.0
                try:
                    inpc_factor = rec.inpc_mitad / rec.inpc_adquisicion
                except:
                    inpc_factor = 0.0
                rec.inpc_factor =  inpc_factor
                if rec.asset_id:
                    # value = rec.asset_id.value_residual
                    try:
                        value = rec.asset_id.value - rec.asset_id.value_residual
                    except:
                        value = rec.asset_id.value_residual
                    rec.inpc_depresiacion = inpc_factor * value
            # Al final escribimos el resultado en el Activo ###
            if rec.asset_id:
                rec.asset_id.inpc_mitad = rec.inpc_mitad
                rec.asset_id.inpc_adquisicion = rec.inpc_adquisicion
                rec.asset_id.inpc_factor = rec.inpc_factor
                rec.asset_id.inpc_depresiacion = rec.inpc_depresiacion
                rec.asset_id.last_asset_control_id = rec.id
            if rec.inpc_depresiacion:
                rec.compute_done = True
        ### BORRAR ###
        return True
        #raise UserError("Calculando el INPC para el activo")