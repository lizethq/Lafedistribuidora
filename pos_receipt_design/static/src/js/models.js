/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_receipt_design.models', function (require) {
    "use strict"
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PosDB = require("point_of_sale.DB");
    var Printer = require('point_of_sale.Printer').Printer;
    var rpc = require('web.rpc');

    models.load_models([{
        model: 'receipt.design',
        loaded: function(self, designs) {
            self.db.all_designs = designs;
            self.db.receipt_by_id = {};
            designs.forEach(function(design){
                self.db.receipt_by_id[design.id] = design;
            });
        },
    }])

    PosDB.include({
        init: function(options){
            var self = this;
            this._super(options);
            this.receipt_design = null;
        },
    })

    screens.ReceiptScreenWidget.include({
        render_receipt: function() {
            var self = this;
            if(!self.pos.config.use_custom_receipt){
                this._super();
            }
            else{
                var receipt_design_id = self.pos.config.receipt_design_id[0]
                var receipt_design = self.pos.db.receipt_by_id[receipt_design_id].receipt_design
                var order = self.pos.get_order();
    
                var data = {
                    widget: this,
                    pos: order.pos,
                    order: order,
                    receipt: order.export_for_printing(),
                    orderlines: order.get_orderlines(),
                    paymentlines: order.get_paymentlines(),
                };
    
                var parser = new DOMParser();
                var xmlDoc = parser.parseFromString(receipt_design,"text/xml");

                var s = new XMLSerializer();
                var newXmlStr = s.serializeToString(xmlDoc);
		
		//Works using the DOMParser
                var qweb = new QWeb2.Engine();
                qweb.add_template('<templates><t t-name="receipt_design">'+newXmlStr+'</t></templates>');

		// Also works without using the DOMParser
                // var qweb = new QWeb2.Engine();
                // qweb.add_template('<templates><t t-name="receipt_design">'+receipt_design+'</t></templates>');

                var receipt = qweb.render('receipt_design',data) ;
                this.$('.pos-receipt-container').html(receipt);
            }
        },
    })

    screens.PaymentScreenWidget.include({
        send_receipt_to_customer: function(order_server_ids) {
            var self = this;
            if(!self.pos.config.use_custom_receipt){
                return this._super(order_server_ids);
            }
            else{
                var order = this.pos.get_order();
                var data = { widget: this,
                    pos: order.pos,
                    order: order,
                    receipt: order.export_for_printing(),
                    orderlines: order.get_orderlines(),
                    paymentlines: order.get_paymentlines(), };
        
                var receipt_design_id = self.pos.config.receipt_design_id[0]
                var receipt_design = self.pos.db.receipt_by_id[receipt_design_id].receipt_design
    
                var parser = new DOMParser();
                var xmlDoc = parser.parseFromString(receipt_design,"text/xml");

                var s = new XMLSerializer();
                var newXmlStr = s.serializeToString(xmlDoc);
		
                var qweb = new QWeb2.Engine();
                qweb.add_template('<templates><t t-name="receipt_design">'+newXmlStr+'</t></templates>');
                
                var receipt = qweb.render('receipt_design',data);
                var printer = new Printer();
        
                return new Promise(function (resolve, reject) {
                    printer.htmlToImg(receipt).then(function(ticket) {
                        rpc.query({
                            model: 'pos.order',
                            method: 'action_receipt_to_customer',
                            args: [order.get_name(), order.get_client(), ticket, order_server_ids],
                        }).then(function() {
                            resolve();
                        }).catch(function () {
                            order.set_to_email(false);
                            reject("There is no internet connection, impossible to send the email.");
                        });
                    });
                });
            }
        },
    })
});
