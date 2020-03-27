/*
    © 2017-2018 Savoir-faire Linux <https://savoirfairelinux.com>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
*/
odoo.define('disable_quick_create', function(require) {
    "use strict";

    var relational_fields = require('web.relational_fields');
    var rpc = require('web.rpc');

    var model_deferred = $.Deferred();
    var models = ['res.partner'];
      var session = require('web.session');
 console.log("hi...."+ session.uid);

    rpc.query({
        model: "res.users",
        method: "search_read",
        args:[
            [['id', '=', session.uid]],
        ],
    }).then(function(result) {
    console.log("hi....");
console.log(result[0])
         console.log(result[0]["disable_create_edit"]);
         var dis=result[0]["disable_create_edit"];
         if(dis ==false){

          relational_fields.FieldMany2One.include({
        init: function() {
            this._super.apply(this, arguments);

            this.nodeOptions.no_quick_create = false;

            if (models.includes(this.field.relation)){
                this.nodeOptions.no_create_edit = false;
            }
        },
    });
         }
         else {
          relational_fields.FieldMany2One.include({
        init: function() {
            this._super.apply(this, arguments);

            this.nodeOptions.no_quick_create = true;

            if (models.includes(this.field.relation)){
                this.nodeOptions.no_create_edit = true;
            }
        },
    });
         }
//        model_deferred.resolve();
    });


});
