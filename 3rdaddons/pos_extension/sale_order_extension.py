'''
Created on Nov 10, 2013

@author: win764
'''
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import locale


class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def _get_date_for_email(self, cr, uid, ids, field_name, arg, context=None):
        reads = self.browse(cr, uid, ids, context)   
        result = {}     
        for obj in reads:        
            utc = datetime.strptime( obj.date_order,'%Y-%m-%d')
            #FIXME: can we read timezone from context?            
            #if 'tz' in context:            
            #    to_zone = tz.gettz(context['tz'])
            #else:
            #TODO: Make formating here
            result[obj.id] = "%s" % utc.strftime('%d-%b-%Y')
        return result
    
    def _get_amount_for_email(self, cr, uid, ids, field_name, arg, context=None):
        reads = self.browse(cr, uid, ids, context)   
        result = {}     
        
        for obj in reads:        
            locale.setlocale( locale.LC_ALL, '' )
            utc = locale.currency(obj.amount_total, symbol=False, grouping=True)
            #FIXME: can we read timezone from context?            
            #if 'tz' in context:            
            #    to_zone = tz.gettz(context['tz'])
            #else:
            #TODO: Make formating here
            result[obj.id] = "%s" % utc
        return result
    
    _columns = {'indo_date' : fields.function(_get_date_for_email, type='char', readonly=True, string='Indo Date'),
                'amt_all' : fields.function(_get_amount_for_email, type='char', readonly=True, string='AMT All'),
                }
    
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    def _get_unit_price_for_email(self, cr, uid, ids, field_name, arg, context=None):
        reads = self.browse(cr, uid, ids, context)   
        result = {}     
        
        for obj in reads:        
            locale.setlocale( locale.LC_ALL, '' )
            utc = locale.currency(obj.price_unit, symbol=False, grouping=True)
            #FIXME: can we read timezone from context?            
            #if 'tz' in context:            
            #    to_zone = tz.gettz(context['tz'])
            #else:
            #TODO: Make formating here
            result[obj.id] = "%s" % utc
        return result
    
    _columns = {
                'indo_price_unit' : fields.function(_get_unit_price_for_email, type='char', readonly=True, string='indo_price_unit'),
                }