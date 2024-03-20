# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools

import datetime
from datetime import datetime
import pytz
from odoo import models

import os

import tempfile
import base64

from odoo.modules import module

import logging
_logger = logging.getLogger(__name__)

class AssetINPCReportXls(models.AbstractModel):
    _name = 'report.l10n_mx_fiscal_depreciations.export_data_asset.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def b64str_to_tempfile(self, b64_str=None, file_suffix=None, file_prefix=None):
        """
        @param b64_str : Text in Base_64 format for add in the file
        @param file_suffix : Sufix of the file
        @param file_prefix : Name of file in TempFile
        """
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodestring(b64_str or str.encode('')))
        f.close()
        os.close(fileno)
        return fname


    def logo_b64_str_to_physical_file(self, b64_str, file_extension='png', prefix='company_logo'):
        _logger.info("\n####################### logo_b64_str_to_physical_file >>>>>>>>>>> ")
        _logger.info("\n####################### file_extension %s " % file_extension)
        _logger.info("\n####################### prefix %s " % prefix)
        certificate_lib = self.env['facturae.certificate.library']
        # b64_temporal_route = certificate_lib.b64str_to_tempfile(base64.encodestring(b''), 
        #                                                   file_suffix='.%s' % file_extension, 
        #                                                   file_prefix='odoo_%s_' % prefix)
        b64_temporal_route = self.b64str_to_tempfile(base64.encodestring(b''), 
                                                          file_suffix='.%s' % file_extension, 
                                                          file_prefix='odoo__%s__' % prefix)
        _logger.info("\n### b64_temporal_route %s " % b64_temporal_route)
        ### Guardando el Logo  ###
        f = open(b64_temporal_route, 'wb')
        f.write(b64_str)
        f.close()

        file_result = open(b64_temporal_route, 'rb').read()
        
        return file_result, b64_temporal_route

    def generate_xlsx_report(self, workbook, data, lines):
        cr = self.env.cr
        depreciacion_line_obj = self.env['account.asset.depreciation.line']
        ## Format para moneda
        num_format = '$ #,##0.0000'
        bg_gray = '#D8D8D8'

        monetary_format =  workbook.add_format({'num_format': '$ #,##0.00'})

        company = self.env.user.company_id
        company_logo = company.logo
        company_logo = base64.b64decode(company_logo)

        if company_logo:
            file_result_b64, logo_path_b64 = self.logo_b64_str_to_physical_file(company_logo, 'png', 'company_logo')
            image_module_path = logo_path_b64
        else:
            module_path = module.get_module_path('l10n_mx_fiscal_depreciations')
            image_module_path = module_path+'/static/img/logo.jpg'

        format_period_title = workbook.add_format({
                                'bold':     True,
                                'align':    'center',
                                'valign':   'vcenter',
                            })

        format_period_title.set_font_size(18)
        format_period_title.set_bottom(2)
        format_period_title.set_top(2)

        format_period_subtitle = workbook.add_format({
                                'bold':     True,
                                'align':    'center',
                                'valign':   'vcenter',
                            })

        format_period_subtitle.set_font_size(14)
        format_period_subtitle.set_bottom(2)
        format_period_subtitle.set_top(2)

        format_bold_border = workbook.add_format({'bold': True, 'valign':   'vcenter'})
        format_bold_border.set_border(2)

        format_bold_border_tit_gray = workbook.add_format({'bold': True, 'valign':   'vcenter'})
        format_bold_border_tit_gray.set_border(2)
        format_bold_border_tit_gray.set_bg_color(bg_gray)

        f_wh_detail_save = workbook.add_format({'bold': True, 'valign':   'vcenter',  'align':   'center'})

        f_gray_detail_save = workbook.add_format({'bold': True, 'valign':   'vcenter',})
        f_gray_detail_save.set_border(2)
        f_gray_detail_save.set_bg_color(bg_gray)


        f_gray_detail_save_center = workbook.add_format({'bold': True, 'valign':   'vcenter', 'align':   'center'})
        f_gray_detail_save_center.set_border(2)
        f_gray_detail_save_center.set_bg_color(bg_gray)

        line_save_right_bold = workbook.add_format({ 'bold': True, 'valign':   'vcenter', 'align':   'right'})
        line_save_right_bold.set_border(2)
        line_save_right_bold.set_bg_color(bg_gray)

        line_save_center_simple = workbook.add_format({'valign':   'vcenter', 'align':   'center', 'num_format': '$ #,##0.00'})

        line_save_center = workbook.add_format({'valign':   'vcenter', 'align':   'center'})
        line_save_center.set_border(1)

        line_save_center_money = workbook.add_format({'valign':   'vcenter', 'align':   'center', 'num_format': '$ #,##0.00'})
        line_save_center_money.set_border(1)

        line_save_center_percentage = workbook.add_format({'valign':   'vcenter', 'align':   'center',})
        line_save_center_percentage.set_border(1)
        line_save_center_percentage.set_num_format(10)  # Same as #,##0

        f_blue_detail_save_center = workbook.add_format({'bold': True, 'valign':   'vcenter', 'align':   'center'})
        f_blue_detail_save_center.set_border(2)
        f_blue_detail_save_center.set_font_color('white')
        f_blue_detail_save_center.set_bg_color("#3465a4")

        format_bold_border2 = workbook.add_format({'bold': True, 'valign':   'vcenter', 'align':   'center'})
        format_bold_border2.set_border(2)

        format_bold_border_monetary = workbook.add_format({'bold': True, 'valign':   'vcenter', 'align':   'center', 'num_format': '$ #,##0.00'})
        format_bold_border_monetary.set_border(2)


        format_bold_border_bg_yllw = workbook.add_format({'bold': True, 'valign':   'vcenter', 'align':   'center'})
        format_bold_border_bg_yllw.set_border(2)
        format_bold_border_bg_yllw.set_bg_color("#F0FF5B")

        format_bold_border_bg_gray = workbook.add_format({'bold': True, 'valign':   'vcenter', 'align':   'center'})
        format_bold_border_bg_gray.set_border(2)
        format_bold_border_bg_gray.set_bg_color(bg_gray)

        format_header_border_bg_gray = workbook.add_format({'bold': True, 'valign':   'vcenter', 'align':   'center', 'text_wrap': True})
        format_header_border_bg_gray.set_border(2)
        format_header_border_bg_gray.set_bg_color(bg_gray)
        format_header_border_bg_gray.set_font_size(12)

        format_bold_border_bg_yllw_line = workbook.add_format({'bold': True, 'valign':   'vcenter', 'align':   'center'})
        format_bold_border_bg_yllw_line.set_border(1)
        format_bold_border_bg_yllw_line.set_bg_color("#F0FF5B")
        format_bold_border_bg_yllw_line.set_font_size(9)


        format_bold_border_bg_wht_line = workbook.add_format({'valign':   'vcenter', 'align':   'center'})
        format_bold_border_bg_wht_line.set_border(1)
        format_bold_border_bg_wht_line.set_font_size(9)


        format_bold_border_bg_wht_line_boxes = workbook.add_format({'valign':   'vcenter', 'align':   'center'})
        format_bold_border_bg_wht_line_boxes.set_border(1)
        format_bold_border_bg_wht_line_boxes.set_bg_color(bg_gray)
        format_bold_border_bg_wht_line_boxes.set_font_size(9)

        format_bold_border_bg_wht_line_left = workbook.add_format({'valign':   'vcenter', 'align':   'left'})
        format_bold_border_bg_wht_line_left.set_border(1)
        format_bold_border_bg_wht_line_left.set_font_size(9)

        format_bold_border_bg_wht_signs = workbook.add_format({'align':   'center', 'bold': True})
        format_bold_border_bg_wht_signs.set_border(1)
        format_bold_border_bg_wht_signs.set_font_size(9)

        banxico_data = self.env['banxico.inpc.data']
        banxico_data_open_id = banxico_data.search([('state','=','process')], limit=1)

        sheet = workbook.add_worksheet('Reporte INPC')
        sheet.set_column('A:B', 28)
        sheet.set_column('C:L', 24)

        sheet.insert_image('A1', image_module_path, {'x_scale': 0.13, 'y_scale': 0.13})
        sheet.write('F3','COMPAÑIA:',format_bold_border_tit_gray)
        sheet.write('F4','RFC:',format_bold_border_tit_gray)
        sheet.write('F5','AÑO:',format_bold_border_tit_gray)

        sheet.write('F6','FECHA:',format_bold_border_tit_gray)
        sheet.write('F7','PERIODO ACTUAL:',format_bold_border_tit_gray)
        sheet.write('F8','INPC ACTUAL:',format_bold_border_tit_gray)

        sheet.merge_range('G3:H3',company.name,format_bold_border2)
        sheet.merge_range('G4:H4',company.vat,format_bold_border2)
        sheet.merge_range('G5:H5',banxico_data_open_id.year_id.name,format_bold_border2)
        # sheet.merge_range('G4:H4',format_bold_border2)

        fecha_creacion = str(fields.Date.context_today(self))
        fecha_creacion_sp = fecha_creacion.split('-')
        fecha_creacion = fecha_creacion_sp[2]+'/'+fecha_creacion_sp[1]+'/'+fecha_creacion_sp[0]
        sheet.merge_range('G6:H6',str(fecha_creacion),format_bold_border_bg_gray)
        sheet.merge_range('G7:H7', banxico_data_open_id.current_period.name, format_bold_border2)
        sheet.merge_range('G8:H8', banxico_data_open_id.inpc_current, format_bold_border_monetary)

        sheet.merge_range('C4:D6', 'CUADRO DE DEPRECIACIÓN',format_period_title)

        i = 11
        ######## Totales Ahorros #########
        year_period_date = banxico_data_open_id.year_id.date_start
        year_period = int(year_period_date.year)
        before_year = year_period - 1 

        sheet.write('A%s' % i,' DESC ACTIVO',f_gray_detail_save_center)
        sheet.write('B%s' % i,' FECHA DE ADQ',f_gray_detail_save_center)
        sheet.write('C%s' % i,' MOI',f_gray_detail_save_center)
        sheet.write('D%s' % i,' TASA',f_gray_detail_save_center)
        sheet.write('E%s' % i,' DEP ACUMULADA %s' % str(before_year),f_gray_detail_save_center)
        sheet.write('F%s' % i,' DEP EJERCICIO',f_gray_detail_save_center)
        sheet.write('G%s' % i,' DEP ACUMULADA %s' % banxico_data_open_id.year_id.name,f_gray_detail_save_center)
        sheet.write('H%s' % i,' MOI POR DEDUCIR',f_gray_detail_save_center)
        sheet.write('I%s' % i,' INPC MITAD PERIODO',f_gray_detail_save_center)
        sheet.write('J%s' % i,' INPC FECHA ADQ',f_gray_detail_save_center)
        sheet.write('K%s' % i,' DEP EJ ACTUALIZADA',f_gray_detail_save_center)
        i+=1
        ## Acumulando Totales ##
        value_global = 0.0
        depreciacion_anterior_global = 0.0
        depreciacion_ejercicio_global = 0.0
        depreciacion_acum_y_global = 0.0
        moi_por_deducir_global = 0.0
        inpc_depresiacion_global = 0.0
        for rec in lines:
            date_asset = str(rec.date)
            date_asset_p = date_asset.split('-')
            date_asset_f  = date_asset_p[2]+'/'+date_asset_p[1]+'/'+date_asset_p[0]
            date_acquirer = rec.date
            acquirer_year = date_acquirer.year
            acquirer_month = date_acquirer.month
            acquirer_month_str = str(acquirer_month)
            if acquirer_month <= 10:
                acquirer_month_str = '0%s' % str(int(acquirer_month))
            depreciacion_anterior = 0.0
            if acquirer_year < year_period:
                date_prev_start = '%s-01-01' % acquirer_year
                date_prev_stop = '%s-12-31' % acquirer_year
                cr.execute("""
                    select depreciated_value from account_asset_depreciation_line
                        where asset_id = %s and depreciation_date between %s and %s
                        order by id desc limit 1;
                    """, (rec.id, date_prev_start, date_prev_stop))
                cr_res = cr.fetchall()
                if cr_res and cr_res[0] and cr_res[0][0]:
                    depreciacion_anterior = cr_res[0][0]

            depreciacion_acum_y = 0.0
            date_prev_start = '%s-01-01' % year_period
            date_prev_stop = '%s-12-31' % year_period
            cr.execute("""
                select depreciated_value from account_asset_depreciation_line
                    where asset_id = %s and depreciation_date between %s and %s
                    order by id desc limit 1;
                """, (rec.id, date_prev_start, date_prev_stop))
            cr_res = cr.fetchall()
            if cr_res and cr_res[0] and cr_res[0][0]:
                depreciacion_acum_y = cr_res[0][0]

            depreciacion_ejercicio = 0.0
            date_prev_start = '%s-01-01' % year_period
            date_prev_stop = '%s-12-31' % year_period
            cr.execute("""
                select sum(amount) from account_asset_depreciation_line
                    where asset_id = %s and depreciation_date between %s and %s;
                """, (rec.id, date_prev_start, date_prev_stop))
            cr_res = cr.fetchall()
            if cr_res and cr_res[0] and cr_res[0][0]:
                depreciacion_ejercicio = cr_res[0][0]

            moi_por_deducir = 0.0
            if depreciacion_ejercicio > 0.0:
                moi_por_deducir = rec.value - depreciacion_ejercicio
            sheet.write('A%s' % i, rec.name, line_save_center)
            sheet.write('B%s' % i, date_asset_f, line_save_center)
            sheet.write('C%s' % i, rec.value, line_save_center_money)
            sheet.write('D%s' % i, 0.30, line_save_center_percentage)
            sheet.write('E%s' % i, depreciacion_anterior, line_save_center_money)
            sheet.write('F%s' % i, depreciacion_ejercicio, line_save_center_money)
            sheet.write('G%s' % i, depreciacion_acum_y, line_save_center_money)
            sheet.write('H%s' % i, moi_por_deducir, line_save_center_money)
            sheet.write('I%s' % i, rec.inpc_mitad, line_save_center)
            sheet.write('J%s' % i, rec.inpc_adquisicion, line_save_center)
            sheet.write('K%s' % i, rec.inpc_depresiacion, line_save_center_money)

            value_global = value_global + rec.value
            depreciacion_anterior_global = depreciacion_anterior_global + depreciacion_anterior
            depreciacion_ejercicio_global = depreciacion_ejercicio_global + depreciacion_ejercicio
            depreciacion_acum_y_global = depreciacion_acum_y_global + depreciacion_acum_y
            moi_por_deducir_global = moi_por_deducir_global + moi_por_deducir
            inpc_depresiacion_global = inpc_depresiacion_global + rec.inpc_depresiacion

            i+=1
        #### Grabando los Totales ####
        i+=1
        sheet.write('B%s' % i, "Total ", line_save_right_bold)
        sheet.write('C%s' % i, value_global, line_save_center_simple)
        sheet.write('E%s' % i, depreciacion_anterior_global, line_save_center_simple)
        sheet.write('F%s' % i, depreciacion_ejercicio_global, line_save_center_simple)
        sheet.write('G%s' % i, depreciacion_acum_y_global, line_save_center_simple)
        sheet.write('H%s' % i, moi_por_deducir_global, line_save_center_simple)
        sheet.write('K%s' % i, inpc_depresiacion_global, line_save_center_simple)
        i+=1

