# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2021 German Ponce Dominguez
#
##############################################################################

from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.tools import float_repr, format_datetime
from odoo.tools.misc import get_lang
from odoo.exceptions import ValidationError, UserError

from odoo.tools import float_is_zero, float_compare
from itertools import groupby
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrderPriceUnitChange(models.Model):
    _name = 'sale.order.price.unit.change'
    _description = 'Cambio de Precio Unitario'

    @api.model
    def default_get(self, default_fields):
        context = self._context
        res = super(SaleOrderPriceUnitChange, self).default_get(default_fields)
        active_ids = context.get('active_ids', [])
        for line in self.env['sale.order.line'].browse(active_ids):
            res.update({'price_unit': line.price_unit})
        return res

    price_unit = fields.Float('Precio Unitario', digits=(14,2))
    
    def execute_price(self):
        context = self.env.context
        active_ids = context.get('active_ids', [])
        for line in self.env['sale.order.line'].browse(active_ids):
            if line.order_id.state not in ('draft','sent','sale','confirmed'):
                raise UserError("No se puede cambiar el precio en el estado actual del pedido.")
            previous_price = line.price_unit
            price_new = self.price_unit
            line.price_unit = price_new
            body_msg = "Actualización de precio.<br/><strong>Producto: </strong>%s<br/><strong>Precio Anterior: </strong>%s<br/><strong>Precio Nuevo: </strong>%s" % (line.product_id.name_get()[0][1], previous_price, price_new)
            line.order_id.message_post(body=body_msg)
        return {'type': 'ir.actions.act_window_close'}