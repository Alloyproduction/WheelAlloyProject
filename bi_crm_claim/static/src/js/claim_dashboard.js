odoo.define('claim_dashboard.dashboard', function (require) {
    "use strict";
    
var core = require('web.core');
var framework = require('web.framework');
var session = require('web.session');
var ajax = require('web.ajax');
var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var AbstractAction = require('web.AbstractAction');
var ControlPanelMixin = require('web.ControlPanelMixin');
var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var CRMDashboardView = AbstractAction.extend(ControlPanelMixin, {
	events: {
        'click .new_claims': 'action_new_claims',
        'click .my_pipeline': 'action_my_pipeline',
        'click .action_confirm': 'action_confirm',
         'click .process_count': 'action_process_count',
        'click .won_count': 'action_won_count',
        'click .loss_count': 'action_loss_count',

	},
	init: function(parent, context) {
        this._super(parent, context);
        var crm_data = [];
        var self = this;
        if (context.tag == 'claim_dashboard.dashboard') {
            self._rpc({
                model: 'crm.claim',
                method: 'get_crm_info',
            }, []).then(function(result){
                self.crm_data = result[0]
            }).done(function(){
                self.render();
                self.href = window.location.href;
            });
        }
    },
    willStart: function() {
         return $.when(ajax.loadLibs(this), this._super());
    },
    start: function() {
        var self = this;
        return this._super();
    },
    render: function() {
        var super_render = this._super;
        var self = this;
        var crm_dashboard = QWeb.render( 'claim_dashboard.dashboard', {
            widget: self,
        });
        $( ".o_control_panel" ).addClass( "o_hidden" );
        $(crm_dashboard).prependTo(self.$el);
        self.graph();
        // self.previewTable();
        return crm_dashboard
    },
    reload: function () {
            window.location.href = this.href;
    },
    action_new_claims: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("New Claims"),
            type: 'ir.actions.act_window',
            res_model: 'crm.claim',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {                        
                        'search_default_by_draft':true,
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_my_pipeline: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("My Pipeline"),
            type: 'ir.actions.act_window',
            res_model: 'crm.claim',
            view_mode: 'tree,form,kanban',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
            context: {                        
                        'search_default_by_MyPipeline':true,
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_confirm: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Confirm Claim"),
            type: 'ir.actions.act_window',
            res_model: 'crm.claim',
            view_mode: 'tree,form,kanban',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
            context: {                        
                        'search_default_by_confirm':true,
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_won_count: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Won"),
            type: 'ir.actions.act_window',
            res_model: 'crm.claim',
             view_mode: 'tree,form,kanban',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
             context: {
                        'search_default_by_won':true,
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_loss_count: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Loss"),
            type: 'ir.actions.act_window',
            res_model: 'crm.claim',
            view_mode: 'tree,form,kanban',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
             context: {
                        'search_default_by_lost':true,
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_process_count: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Process"),
            type: 'ir.actions.act_window',
            res_model: 'crm.claim',
            view_mode: 'tree,form,kanban',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
             context: {
                        'search_default_by_process':true,
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    // Function which gives random color for charts.
    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }

        return color;
    },

    // Here we are plotting bar,pie chart
    graph: function() {
        var self = this
        var ctx = this.$el.find('#Chart')
        // Fills the canvas with white background
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
            //console.log(bg_color_list);
        }
        // add by haytham
        bg_color_list =["#f68370", "#FA9D00" ,"#89DBEC", "#ED0026","#91278F", "#006884"]
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
//                labels: ["January","February", "March", "April", "May", "June", "July", "August", "September"],
                // "October", "November", "December"],
                labels: self.crm_data.graph_exp_revenue_label,
                datasets: [{
                    label: 'Claim States',
                    data: self.crm_data.graph_exp_revenue_dataset,
                    backgroundColor: bg_color_list,
                    borderColor: bg_color_list,
                    borderWidth: 1,
                    pointBorderColor: 'white',
                    pointBackgroundColor: 'red',
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    pointHitRadius: 30,
                    pointBorderWidth: 2,
                    pointStyle: 'rectRounded'
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: Math.max.apply(null,self.crm_data.graph_exp_revenue_dataset),
                            //min: 1000,
                            //max: 100000,
                            stepSize: self.crm_data.
                            graph_exp_revenue_dataset.reduce((pv,cv)=>{return pv + (parseFloat(cv)||0)},0)
                            /self.crm_data.graph_exp_revenue_dataset.length
                          }
                    }]
                },
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 100, // general animation time
                },
                hover: {
                    animationDuration: 500, // duration of animations when hovering an item
                },
                responsiveAnimationDuration: 500, // animation duration after a resize
                legend: {
                    display: true,
                    labels: {
                        fontColor: 'black'
                    }
                },
            },
        });
       

    },
    
});
core.action_registry.add('claim_dashboard.dashboard', CRMDashboardView);
return CRMDashboardView
    
});