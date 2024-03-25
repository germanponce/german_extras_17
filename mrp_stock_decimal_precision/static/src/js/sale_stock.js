odoo.define('fx_sales_product_warehouse_quantity.QtyAtDateWidgetExtend', function (require) {
"use strict";

var core = require('web.core');
var QWeb = core.qweb;

var Widget = require('web.Widget');
var widget_registry = require('web.widget_registry');
var utils = require('web.utils');

var _t = core._t;
var time = require('web.time');

const QtyAtDateWidget = require('sale_stock.QtyAtDateWidget');


var QtyAtDateWidgetExtend = QtyAtDateWidget.extend({
    _getContent() {
        console.log("### this.data.scheduled_date >>> ",this.data.scheduled_date);
        if (this.data.scheduled_date) {
            this.data.delivery_date = this.data.scheduled_date.clone().add(this.getSession().getTZOffset(this.data.scheduled_date), 'minutes').format(time.getLangDateFormat());
            if (this.data.forecast_expected_date) {
                this.data.forecast_expected_date_str = this.data.forecast_expected_date.clone().add(this.getSession().getTZOffset(this.data.forecast_expected_date), 'minutes').format(time.getLangDateFormat());
            }
        }
        
        const $content = $(QWeb.render('sale_stock.QtyDetailPopOver', {
            data: this.data,
        }));
        $content.on('click', '.action_open_forecast', this._openForecast.bind(this));
        return $content;
    },
});

widget_registry.add('qty_at_date_widget', QtyAtDateWidgetExtend);

return QtyAtDateWidgetExtend;
});
