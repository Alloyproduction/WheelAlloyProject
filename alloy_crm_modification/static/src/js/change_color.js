
odoo.define('alloy_crm_modification.Change_color', function (require) {
	"use strict";
var AbstractField = require('web.AbstractField');
var core = require('web.core');
var field_registry = require('web.field_registry');
var time = require('web.time');

var _t = core._t;
var xduration=0;
var xendduration=0;
var counter=0;



var ChangeColor = AbstractField.extend({
    supportedFieldTypes: [],
//    init: function(){
//
//  console.log($record);
//  console.log("hello zaki");
//    },

    willStart: function () {
        var self = this;
		var nowDate = new Date();

//		console.log($record );
//		var before6day= nowDate ;
//		 before6day.setDate( nowDate.getDate() -10 );
//		console.log(before6day);
        var def = this._rpc({
            model: 'crm.lead',
            method: 'search_read',
            domain: [
                ['is_lost', '=', 'True'],

            ],
        }).then(function (result) {
            if (self.mode === 'readonly') {
                var currentDate = new Date();

                self.duration = 0;
                self.Eduration=0;
                _.each(result, function (data) {
                xendduration = self._getDateDifference(currentDate,data.date_deadline);
                self.Eduration +=xendduration;
                xendduration=xendduration/(60*60*1000);
//                   console.log(" hi.. willStart");
                //  console.log(data.production_id);
                 //   console.log(data.date_start);
                 //  console.log(data.date_deadline);
                 //  console.log(currentDate);
                 //   console.log(xendduration);
                //   console.log("-------------------------------------");

                        self.duration += data.date_end ?
                        self._getDateDifference(data.date_start, data.date_end) :
                        self._getDateDifference(time.auto_str_to_date(data.date_start), currentDate);
                });
            }
        });
//		console.log(def);

        return $.when(this._super.apply(this, arguments), def);
    },
    destroy: function () {
        this._super.apply(this, arguments);
        clearTimeout(this.timer);
    },
    isSet: function () {
        return true;
    },
    _getDateDifference: function (dateStart, dateEnd) {
        return moment(dateEnd).diff(moment(dateStart));
    },


 _render: function () {
        this._startTimeCounter();
    },
    _startTimeCounter: function () {
        var self = this;
//        console.log (this.record.data.is_lost ) ##1e8dee #0cf592 .parent().parent().parent()
        if (this.record.data.is_lost_blue == true){
          this.$el.parent().parent().parent().parent().css("background-color", '#f58590' );
          this.$el.parent().parent().parent().parent().css("color", '#000000' );
          }
          if (this.record.data.is_lost_green == true){
          this.$el.parent().parent().parent().parent().css("background-color", '#f58000' );
          this.$el.css("color", '#000000' );
          }

    },
});

field_registry
    .add('change_color', ChangeColor);

});
