# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class AccountMove(models.Model):
    _inherit ='account.move'


    def get_invoice_lines_to_number_pages_print(self):
        invoice_details_print_list_dict = []
        # Cada elemento  sera una lista de valores:
        # [{'producto': X, 'cantidad': x}]
        i = 1
        quantity_sumatory = 0
        for line in self.invoice_line_ids:
            quantity_sumatory +=  int(line.quantity)
        for line in self.invoice_line_ids:
            # i = 1
            quantity_line = int(line.quantity)
            quantity = int(line.quantity)
            product = line.product_id            
            while (quantity > 0 ):
                quantity_of = "%s/%s" % (i, quantity_sumatory)
                xvals = {
                            'product': product,
                            'count_n': i,
                            'quantity_line': quantity_line,
                            'quantity_of': quantity_of,
                            'quantity_sumatory': quantity_sumatory,
                        }
                invoice_details_print_list_dict.append(xvals)
                quantity -= 1
                i+=1

        return invoice_details_print_list_dict
