# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import logging
import pdb
import time

import openerp
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

    
class pos_order_line_report(osv.osv):
    _name = "pos.order.line.report"
    _description = "POS Order line Statistics"
    _auto = False
    _rec_name = 'create_date'
    
    
    def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
        res = dict([(i, {}) for i in ids])
        account_tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = line.product_id.taxes_id
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = account_tax_obj.compute_all(cr, uid, line.product_id.taxes_id, price, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)

            cur = line.order_id.pricelist_id.currency_id
            res[line.id]['price_subtotal'] = cur_obj.round(cr, uid, cur, taxes['total'])
            res[line.id]['price_subtotal_incl'] = cur_obj.round(cr, uid, cur, taxes['total_included'])
        return res
    
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'name': fields.char('Line No', size=32, required=True),
        'notice': fields.char('Discount Notice', size=128),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], required=True, change_default=True),
        'price_unit': fields.float(string='Unit Price', digits=(16, 2)),
        'qty': fields.float('Quantity', digits=(16, 2)),
        'price_subtotal': fields.function(_amount_line_all, multi='pos_order_line_amount', string='Subtotal w/o Tax', store=True),
        'price_subtotal_incl': fields.function(_amount_line_all, multi='pos_order_line_amount', string='Subtotal', store=True),
        'discount': fields.float('Discount (%)', digits=(16, 2)),
        'order_id': fields.many2one('pos.order', 'Order Ref', ondelete='cascade'),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'session_id':fields.related('order_id', 'session_id', type='many2one', relation='pos.session' ,string='Session'),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'user_id':fields.related('order_id', 'user_id', type='many2one', relation='res.users' ,string='Salesman'),
        'order_date': fields.date('Create date', readonly=True),
        'order_date_string': fields.char('Order Date', size=15),
        'hours': fields.char('Order Hours', size=10),
        
    }
    _order = 'create_date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'pos_order_line_report')
        cr.execute("""
            create or replace view pos_order_line_report as 
            (SELECT 
               to_char(ol.create_date,'dd-MON-yyyy') AS order_date_string,
               to_char(ol.create_date,'HH') AS hours,
               ol.create_date::TIMESTAMP::DATE AS order_date,
               od.partner_id,
               ol.id,ol.create_uid,ol.create_date,ol.write_date,
                     ol.write_uid,ol.notice,ol.product_id,ol.order_id,
                     ol.price_unit,ol.price_subtotal,ol.company_id,
                     ol.price_subtotal_incl,ol.qty,ol.discount,ol.name
                FROM pos_order_line ol
                inner join pos_order od on ol.order_id = od.id)

        """)
pos_order_line_report()
    
    
    




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
