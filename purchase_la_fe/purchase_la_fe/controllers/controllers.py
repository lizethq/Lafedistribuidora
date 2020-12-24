# -*- coding: utf-8 -*-
# from odoo import http


# class MrpSuprapakExtended(http.Controller):
#     @http.route('/mrp_suprapak_extended/mrp_suprapak_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_suprapak_extended/mrp_suprapak_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_suprapak_extended.listing', {
#             'root': '/mrp_suprapak_extended/mrp_suprapak_extended',
#             'objects': http.request.env['mrp_suprapak_extended.mrp_suprapak_extended'].search([]),
#         })

#     @http.route('/mrp_suprapak_extended/mrp_suprapak_extended/objects/<model("mrp_suprapak_extended.mrp_suprapak_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_suprapak_extended.object', {
#             'object': obj
#         })