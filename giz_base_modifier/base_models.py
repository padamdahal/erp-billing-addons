# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import logging
logger = logging.getLogger(__name__)

# Users
class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True)
    }
res_users()

# Sale Order
class sale_order(osv.osv):
    _inherit = 'sale.order'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(sale_order, self).default_get(cr, uid, fields, context=context)
        shop_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).shop_id
        if shop_id:
            res.update({'shop_id':shop_id.id})
        return res
sale_order()

# Account Invoice
class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _get_default_shop(self, cr, uid, context=None):
        shop_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).shop_id
        if shop_id:
            return shop_id.id
    
    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, states={'draft': [('readonly', False)]})
    }
    
    _defaults = {
        'shop_id': _get_default_shop,
    }
    
    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        logger.info("\n\n\n****Invoice Type=%s",inv.type)
        if inv.type == 'in_invoice':
            amount = amount = inv.partner_id.debit
            logger.info("\n\n\n****inv.partner_id.debit=%s",inv.partner_id.debit)
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            #'url':final_url
            'tag': 'onchange_partner_id',
            'domain': '[]',
            'context': {
                'default_partner_id': inv.partner_id.id,
                'default_reference': inv.name,
                'default_amount': inv.type in ('out_invoice','out_refund') and inv.amount_total or amount,
                'close_after_process': True,
                'invoice_type': inv.type,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'active_ids':'',
                'active_id':inv.id,
            }
        }
account_invoice()

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    def proforma_voucher(self, cr, uid, ids, context=None):
        res = super(account_voucher,self).proforma_voucher(cr, uid, ids, context)
        if isinstance(ids,(list)):
            ids = ids[0]
        self.write(cr, uid, ids, {'state':'posted'}, context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
