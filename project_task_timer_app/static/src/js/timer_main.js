odoo.define('project_task_timer_app.timer_main', function (require) {
	"use strict";
var AbstractField = require('web.AbstractField');
var core = require('web.core');
var field_registry = require('web.field_registry');
var time = require('web.time');

var _t = core._t;
var xduration=0;
var xendduration=0;
var TimeCounter = AbstractField.extend({
    supportedFieldTypes: [],
    
    willStart: function () {
        var self = this;
        var def = this._rpc({
            model: 'project.calculate.duration',
            method: 'search_read',
            domain: [
                ['production_id', '=', this.record.data.id],
                ['user_id', '=', this.getSession().uid],
            ],
        }).then(function (result) {
            if (self.mode === 'readonly') {
                var currentDate = new Date();

                self.duration = 0;
                self.Eduration=0;
                _.each(result, function (data) {
                xendduration = self._getDateDifference(currentDate,data.date_deadline);
                self.Eduration +=xendduration;
//                xendduration=xendduration/(60*60*1000);
//                    console.log(" hi..");
//                 console.log(data.production_id);
//                   console.log(data.date_start);
//                  console.log(data.date_deadline);
//                   console.log(currentDate);
//                   console.log(xendduration);
//                    console.log("-------------------------------------");

                              self.duration += data.date_end ?
                        self._getDateDifference(data.date_start, data.date_end) :
                        self._getDateDifference(time.auto_str_to_date(data.date_start), currentDate);
                });
            }
        });
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
        clearTimeout(this.timer);
        if (this.record.data.is_user_working) {
            this.timer = setTimeout(function () {
                self.duration += 1000;
                self._startTimeCounter();
            }, 1000);
        } else {
            clearTimeout(this.timer);
        }

         xduration=this.Eduration ;
//         xendduration= xendduration/(60*60*1000);

//
//         if( xendduration <=16 ){
//
//            var $record = this.$el.parent().parent().parent().parent().css("background-color", '#f58590' );
//
//         }
//         else if (xendduration >16 && xendduration < 85 ){
//            var $record = this.$el.parent().parent().parent().parent().css("background-color", '#feffbb' );
//         }
        console.log("hi..");
        console.log(this.Eduration/(60*60*1000));
        xendduration =this.Eduration/(60*60*1000);
         if( xendduration <=16 ){
            var $record = this.$el.parent().parent().parent().parent().css("background-color", '#f58590' );
         }
         else if (xendduration >16 && xendduration < 50 ){
            var $record = this.$el.parent().parent().parent().parent().css("background-color", '#feffbb' );
         }

        this.$el.html($('<span style="color:red;">' + moment.utc(this.duration).format("HH:mm:ss") + '</span>'));
    },
});

field_registry
    .add('task_time_counter', TimeCounter);

});