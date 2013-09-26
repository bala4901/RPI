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
import openerp.addons.product.product

_logger = logging.getLogger(__name__)


import io, StringIO

class ean_wizard(osv.osv_memory):
    _name = 'pos.ean_wizard'
    _columns = {
        'ean13_pattern': fields.char('Reference', size=32, required=True, translate=True),
    }
    def sanitize_ean13(self, cr, uid, ids, context):
        for r in self.browse(cr,uid,ids):
            ean13 = openerp.addons.product.product.sanitize_ean13(r.ean13_pattern)
            m = context.get('active_model')
            m_id =  context.get('active_id')
            self.pool[m].write(cr,uid,[m_id],{'ean13':ean13})
        return { 'type' : 'ir.actions.act_window_close' }

class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'available_in_mrppos': fields.boolean('Available in the Mrp Pos', help='Check if you want this product to appear in the Point of Sale'), 
        'to_weight' : fields.boolean('To Weight', help="Check if the product should be weighted (mainly used with self check-out interface)."),
    }

    _defaults = {
        'to_weight' : False,
        'available_in_mrppos': False,
    }

    def edit_ean(self, cr, uid, ids, context):
        return {
            'name': _("Assign a Custom EAN"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.ean_wizard',
            'target' : 'new',
            'view_id': False,
            'context':context,
        }
        
class mrppos_order(osv.osv):
    _name = "mrppos.order"
    _description = "MRP Point of Sale"
    _order = "id desc"

    def create_from_ui(self, cr, uid, orders, context=None):

        order_ids = []
        for tmp_order in orders:
            order = tmp_order['data']
            order_id = self.create(cr, uid, {
                'name': order['name'],
                'user_id': order['user_id'] or False,
                'lines': order['lines'],
            }, context)
            order_ids.append(order_id)
        #self.create_picking(cr, uid, order_ids, context=context)
        return order_ids


    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ('draft','cancel'):
                raise osv.except_osv(_('Unable to Delete !'), _('In order to delete a sale, it must be new or cancelled.'))
        return super(pos_order, self).unlink(cr, uid, ids, context=context)


    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        d = {
            'state': 'draft',
            'nb_print': 0,
            'name': self.pool.get('ir.sequence').get(cr, uid, 'mrppos.order'),
        }
        d.update(default)
        return super(mrppos_order, self).copy(cr, uid, id, d, context=context)
    
    def _amount_qty(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {'amount_qty': 0.0}
            
            for line in order.lines:
                res[order.id]['amount_qty'] += line.qty

        return res

    _columns = {
        'name': fields.char('Order Name', size=64, required=True, readonly=True),
        'company_id':fields.many2one('res.company', 'Company', required=True, readonly=True),
        'date_order': fields.datetime('Order Date', readonly=True, select=True),
        'user_id': fields.many2one('res.users', 'Salesman', help="Person who uses the the cash register. It can be a reliever, a student or an interim employee."),
        'lines': fields.one2many('mrppos.order.line', 'order_id', 'Order Lines', states={'draft': [('readonly', False)]}, readonly=True),
        'state': fields.selection([('draft', 'New'),
                                   ('cancel', 'Cancelled'),
                                   ('done', 'Confirm')],
                                  'Status', readonly=True),
        'note': fields.text('Internal Notes'),
        'nb_print': fields.integer('Number of Print', readonly=True),
        'prodlot_id' : fields.many2one('stock.production.lot', 'Lot no'),
        'amount_qty': fields.function(_amount_qty, string='Total Qty',  multi='all'),
        'mrp_id': fields.many2one('mrp.production', 'MRP Production', ondelete='cascade'),
    }

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
        'state': 'draft',
        'date_order': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'nb_print': 0,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

    def create(self, cr, uid, values, context=None):
        values['name'] = self.pool.get('ir.sequence').get(cr, uid, 'mrppos.order')
        return super(mrppos_order, self).create(cr, uid, values, context=context)
    
    def action_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'}, context=context)
    
    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)
    


class mrppos_order_line(osv.osv):
    _name = "mrppos.order.line"
    _description = "Lines of Mrp Pos"
    _rec_name = "product_id"


    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'name': fields.char('Line No', size=32, required=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], required=True, change_default=True),
        'qty': fields.float('Quantity', digits=(16, 2)),
        'order_id': fields.many2one('mrppos.order', 'Order Ref', ondelete='cascade'),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'prodlot_id' : fields.many2one('stock.production.lot', 'Lot No', ondelete='cascade'),
    }

    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'mrppos.order.line'),
        'qty': lambda *a: 1,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'mrppos.order.line')
        })
        return super(pos_order_line, self).copy_data(cr, uid, id, default, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
