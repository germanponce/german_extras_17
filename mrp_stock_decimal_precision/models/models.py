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

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class MrpBomLine(models.Model):
    _inherit ='mrp.bom.line'

    product_qty = fields.Float(
        'Cantidad', default=1.0,
        digits='Bom Line Quantity (MRP)', required=True,
        help="This should be the smallest quantity that this product can be produced in. If the BOM contains operations, make sure the work center capacity is accurate.")
    

class StockMove(models.Model):
    _inherit = "stock.move"

    product_qty = fields.Float(
        'Cantidad real', compute='_compute_product_qty', inverse='_set_product_qty',
        digits='Stock Move Real Quantity (MRP)', store=True, compute_sudo=True,
        help='Quantity in the default UoM of the product')

    product_uom_qty = fields.Float(
        'Demanda',
        digits='Stock Move Demand Quantity (MRP)',
        default=0, required=True,
        help="This is the quantity of product that is planned to be moved."
             "Lowering this quantity does not generate a backorder."
             "Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")
    quantity = fields.Float(
        'Cantidad', compute='_compute_quantity', digits='Stock Move Quantity (MRP)', inverse='_set_quantity', store=True)

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    quantity = fields.Float(
        'Quantity', digits='Stock Move Line Quantity (MRP)', copy=False, store=True,
        compute='_compute_quantity', readonly=False)
    
    quantity_product_uom = fields.Float(
        'Quantity in Product UoM', digits='Stock Move Quantity UoM (MRP)',
        copy=False, compute='_compute_quantity_product_uom', store=True)